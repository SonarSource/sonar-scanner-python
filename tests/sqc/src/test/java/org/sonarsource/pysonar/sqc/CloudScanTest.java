/*
 * Sonar Scanner Python
 * Copyright (C) 2011-2026 SonarSource Sàrl
 * mailto:info AT sonarsource DOT com
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 3 of the License, or (at your option) any later version.
 * This program is distributed in the hope that it will be useful,
 *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 */
package org.sonarsource.pysonar.sqc;

import com.sonar.orchestrator.MockUserService;
import com.sonar.orchestrator.Orchestrator;
import com.sonar.orchestrator.locator.FileLocation;
import com.sonar.orchestrator.locator.MavenLocation;
import com.sonarsource.users.client.model.RestUser;
import java.io.File;
import java.io.InputStream;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.time.OffsetDateTime;
import java.util.Map;
import java.util.Properties;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TemporaryFolder;
import org.mockserver.socket.PortFactory;
import org.sonarqube.ws.Ce;
import org.sonarqube.ws.Organizations.Organization;
import org.sonarqube.ws.client.HttpConnector;
import org.sonarqube.ws.client.WsClient;
import org.sonarqube.ws.client.WsClientFactories;
import org.sonarqube.ws.client.ce.TaskRequest;
import org.sonarqube.ws.client.organizations.CreateRequest;
import org.sonarqube.ws.client.projectanalyses.SearchRequest;

import static org.awaitility.Awaitility.await;
import static com.sonar.orchestrator.http.HttpCall.ROOT_TOKEN;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

public class CloudScanTest {
  private static final String PROJECT_KEY = "scanpy-sqc-it";

  @Rule
  public TemporaryFolder temporaryFolder = new TemporaryFolder();

  @Test
  public void scansMinimalPythonProjectOnCloud() throws Exception {
    Orchestrator orchestrator = newOrchestrator();
    try {
      orchestrator.install();
      disableDiskWatermark(orchestrator);
      orchestrator.start();
      orchestrator.getFileSourcesService().setSourceLinesResponseFromExpectedCoreOutput("{\"sources\":[{}]}");

      WsClient client = rootClient(orchestrator);
      configureRootUser(orchestrator);
      Organization organization = createOrganization(client);
      client.projects().create(new org.sonarqube.ws.client.projects.CreateRequest()
        .setProject(PROJECT_KEY)
        .setName("pysonar SQC integration test")
        .setVisibility("public")
        .setOrganization(organization.getKey()));

      Path projectDirectory = copySampleProject();
      String scannerOutput = scan(orchestrator, organization, projectDirectory);
      assertTrue(scannerOutput, scannerOutput.contains("Detected languages: [py]"));

      waitForComputeEngine(client, projectDirectory);
      await().atMost(Duration.ofMinutes(2)).pollInterval(Duration.ofSeconds(1)).untilAsserted(() -> {
        var analyses = client.projectAnalyses().search(new SearchRequest().setProject(PROJECT_KEY)).getAnalysesList();
        assertFalse("No SQC analysis was recorded", analyses.isEmpty());
        assertEquals("1.2", analyses.get(0).getProjectVersion());
      });
    } finally {
      orchestrator.stopAll();
    }
  }

  private Orchestrator newOrchestrator() throws Exception {
    String eventPort = String.valueOf(PortFactory.findFreePort());
    File counterFile = temporaryFolder.newFile("async-indexing-counter.txt");
    MavenLocation distribution = MavenLocation.builder()
      .setGroupId("com.sonarsource.sonarcloud")
      .setArtifactId("edition-sonarcloud")
      .setVersion("LATEST_RELEASE")
      .withPackaging("zip")
      .build();
    return Orchestrator.builderEnv()
      .setZipLocation(distribution)
      .addPlugin(FileLocation.of(new File(System.getProperty("sqc.python.plugin"))))
      .setOrchestratorProperty("orchestrator.workspaceDir", System.getProperty("sqc.workspace.dir"))
      .setServerProperty("sonar.es.bootstrap.checks.disable", "true")
      .setServerProperty("sonar.cluster.web.startupLeader", "true")
      .setServerProperty("sonar.jdbc.timeBetweenEvictionRunsMillis", "30000")
      .setServerProperty("muppet.secret.token", "scanpy-sqc-it -STUB")
      .setServerProperty("sonar.event.topic.port", eventPort)
      .withFunction("io.sonarcloud.cleancode.asyncindexing.itrunner.AsyncIssuesIndexerItRunner",
        new File(System.getProperty("sqc.async.indexer")))
      .setFunctionProperty("sonar.event.topic.port", eventPort)
      .setFunctionProperty("sonar.it.indexing.counter.file", counterFile.getAbsolutePath())
      .setOrchestratorProperty("orchestrator.it.indexing.counter.file", counterFile.getAbsolutePath())
      .build();
  }

  private static WsClient rootClient(Orchestrator orchestrator) {
    return WsClientFactories.getDefault().newClient(HttpConnector.newBuilder()
      .url(orchestrator.getServer().getUrl())
      .token(ROOT_TOKEN)
      .build());
  }

  private static void disableDiskWatermark(Orchestrator orchestrator) throws Exception {
    // The test container shares the host disk, whose usage can exceed OpenSearch's default watermark.
    int searchPort = orchestrator.getServer().getSearchPort().orElseThrow();
    HttpRequest request = HttpRequest.newBuilder(URI.create("http://localhost:" + searchPort + "/_cluster/settings"))
      .header("Content-Type", "application/json")
      .PUT(HttpRequest.BodyPublishers.ofString("""
        {"transient":{"cluster.routing.allocation.disk.threshold_enabled":false,"cluster.blocks.create_index":false}}
        """))
      .build();
    HttpResponse<Void> response = HttpClient.newHttpClient().send(request, HttpResponse.BodyHandlers.discarding());
    assertEquals("Could not configure local OpenSearch", 200, response.statusCode());
  }

  private static void configureRootUser(Orchestrator orchestrator) {
    Map<String, String> admin = orchestrator.getDatabase().executeSql("select uuid, uuid_v4 from users where login='admin'").get(0);
    UUID adminId = UUID.fromString(admin.get("UUID_V4"));
    OffsetDateTime now = OffsetDateTime.now();
    orchestrator.getUserService().addUser(new RestUser(adminId, "sonarqube", now, now, admin.get("UUID"), true)
      .login("admin")
      .name("Administrator")
      .externalLogin("admin"));
    orchestrator.getUserService().addRole(new MockUserService.RoleKey(adminId, null, "sqc"), "root");
  }

  private static Organization createOrganization(WsClient client) {
    return client.organizations().create(new CreateRequest()
      .setKey("scanpy-it")
      .setName("pysonar integration tests")
      .setDescription("Local Cloud scan")
      .setUrl("http://localhost"))
      .getOrganization();
  }

  private Path copySampleProject() throws Exception {
    Path source = Path.of(System.getProperty("sqc.sample.dir"));
    Path project = temporaryFolder.newFolder("minimal").toPath();
    Files.createDirectories(project.resolve("src"));
    Files.copy(source.resolve("pyproject.toml"), project.resolve("pyproject.toml"));
    Files.copy(source.resolve("sonar-project.properties"), project.resolve("sonar-project.properties"));
    Files.copy(source.resolve("src/minimal.py"), project.resolve("src/minimal.py"));
    return project;
  }

  private String scan(Orchestrator orchestrator, Organization organization, Path projectDirectory) throws Exception {
    File outputFile = temporaryFolder.newFile("pysonar-output.txt");
    ProcessBuilder processBuilder = new ProcessBuilder(
      "pysonar",
      "--sonar-host-url=" + orchestrator.getServer().getUrl(),
      "-Dsonar.scanner.sonarcloudUrl=" + orchestrator.getServer().getUrl(),
      "-Dsonar.scanner.apiBaseUrl=http://localhost:" + orchestrator.getConfiguration().getAnalysisServicesHttpPort(),
      "--skip-jre-provisioning",
      "-Dsonar.projectKey=" + PROJECT_KEY,
      "-Dsonar.organization=" + organization.getKey(),
      "-Dsonar.plugins.origin=local",
      "--verbose");
    processBuilder.directory(projectDirectory.toFile());
    processBuilder.redirectErrorStream(true);
    processBuilder.redirectOutput(outputFile);
    processBuilder.environment().put("SONAR_TOKEN", ROOT_TOKEN);
    processBuilder.environment().put("SONAR_USER_HOME", temporaryFolder.newFolder("sonar-user-home").getAbsolutePath());
    processBuilder.environment().keySet().removeIf(key -> key.startsWith("GITHUB_"));

    Process process = processBuilder.start();
    boolean finished = process.waitFor(5, TimeUnit.MINUTES);
    if (!finished) {
      process.destroyForcibly();
      fail("pysonar did not finish within five minutes");
    }
    String output = Files.readString(outputFile.toPath());
    assertEquals(output, 0, process.exitValue());
    return output;
  }

  private static void waitForComputeEngine(WsClient client, Path projectDirectory) throws Exception {
    Properties taskProperties = new Properties();
    try (InputStream report = Files.newInputStream(projectDirectory.resolve(".scannerwork/report-task.txt"))) {
      taskProperties.load(report);
    }
    String taskId = taskProperties.getProperty("ceTaskId");
    assertFalse("Scanner report has no CE task ID", taskId == null || taskId.isBlank());

    await().atMost(Duration.ofMinutes(2)).pollInterval(Duration.ofSeconds(1)).until(() -> {
      Ce.Task task = client.ce().task(new TaskRequest().setId(taskId)).getTask();
      Ce.TaskStatus status = task.getStatus();
      if (status == Ce.TaskStatus.FAILED || status == Ce.TaskStatus.CANCELED) {
        fail("CE task ended with " + status + ": " + task.getErrorMessage());
      }
      return status == Ce.TaskStatus.SUCCESS;
    });
  }
}

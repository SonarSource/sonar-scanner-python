plugins {
    java
}

val sonarcloudCoreVersion = providers.gradleProperty("sonarcloudCoreVersion").get()
val asyncIndexer = configurations.create("asyncIndexer") { isTransitive = false }
val pythonPlugin = configurations.create("pythonPlugin") { isTransitive = false }

dependencyLocking {
    lockAllConfigurations()
    lockMode = LockMode.STRICT
}

dependencies {
    asyncIndexer("com.sonarsource.sonarcloud.async-issues-indexer:async-issues-indexer-it-runner:${providers.gradleProperty("asyncIndexerVersion").get()}") {
        artifact { classifier = "jar-with-dependencies" }
    }
    pythonPlugin("com.sonarsource.python:sonar-python-enterprise-plugin:${providers.gradleProperty("pythonPluginVersion").get()}")

    // WireMock's standalone JAR has an older message bundle, so load the matching validator bundle first.
    testImplementation("com.networknt:json-schema-validator:${providers.gradleProperty("schemaValidatorVersion").get()}")
    testImplementation("junit:junit:${providers.gradleProperty("junitVersion").get()}")
    testImplementation("com.sonarsource.sonarcloud:sonar-orchestrator:$sonarcloudCoreVersion") {
        exclude(group = "com.sonarsource.sca", module = "client")
    }
    testImplementation("com.sonarsource.sonarcloud.core:db-migrations-task:$sonarcloudCoreVersion:jar-with-dependencies")
    testImplementation("com.sonarsource.sonarcloud.core:dynamodb-local-initializer:$sonarcloudCoreVersion:jar-with-dependencies")
    testImplementation("com.sonarsource.sonarcloud:sonar-ws:$sonarcloudCoreVersion")
    testImplementation("com.sonarsource.sonarcloud:users-client:$sonarcloudCoreVersion")
    testImplementation("com.sonarsource.sonarcloud:quality-gates-client:$sonarcloudCoreVersion")
    testImplementation("org.mock-server:mockserver-netty:${providers.gradleProperty("mockserverVersion").get()}")
    testImplementation("org.testcontainers:postgresql:${providers.gradleProperty("testcontainersVersion").get()}")
    testImplementation("org.wiremock:wiremock-standalone:${providers.gradleProperty("wiremockVersion").get()}")
    testImplementation("org.awaitility:awaitility:${providers.gradleProperty("awaitilityVersion").get()}")
}

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

tasks.test {
    useJUnit()
    maxHeapSize = "2g"

    systemProperty("sqc.async.indexer", asyncIndexer.singleFile.absolutePath)
    systemProperty("sqc.python.plugin", pythonPlugin.singleFile.absolutePath)
    systemProperty("sqc.sample.dir", rootProject.file("../../tests/its/sources/minimal").absolutePath)
    systemProperty("sqc.workspace.dir", layout.buildDirectory.dir("it").get().asFile.absolutePath)
    systemProperty("orchestrator.artifactory.url", "https://repox.jfrog.io/repox")

    val artifactoryPassword = System.getenv("ARTIFACTORY_PASSWORD")
        ?: providers.gradleProperty("artifactoryPassword").orNull
    if (!artifactoryPassword.isNullOrEmpty()) {
        systemProperty("orchestrator.artifactory.apiKey", artifactoryPassword)
        systemProperty("orchestrator.artifactory.accessToken", artifactoryPassword)
    }

    testLogging {
        events("failed", "skipped")
    }
}

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

import com.sonar.orchestrator.config.Configuration;
import com.sonar.orchestrator.locator.MavenLocation;

public final class SqcDistribution {
  private SqcDistribution() {
  }

  public static MavenLocation location() {
    return MavenLocation.builder()
      .setGroupId("com.sonarsource.sonarcloud")
      .setArtifactId("edition-sonarcloud")
      .setVersion("LATEST_RELEASE")
      .withPackaging("zip")
      .build();
  }

  public static void main(String[] args) {
    String version = Configuration.createEnv().locators().maven().resolveVersion(location())
      .orElseThrow(() -> new IllegalStateException("Could not resolve the latest SQC distribution version"));
    System.out.println("SQC_DISTRIBUTION_VERSION=" + version);
  }
}

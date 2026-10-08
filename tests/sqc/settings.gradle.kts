rootProject.name = "pysonar-sqc-it"

dependencyResolutionManagement {
    val artifactoryUsername = System.getenv("ARTIFACTORY_USERNAME")
        ?: providers.gradleProperty("artifactoryUsername").orNull.orEmpty()
    val artifactoryPassword = System.getenv("ARTIFACTORY_PASSWORD")
        ?: providers.gradleProperty("artifactoryPassword").orNull.orEmpty()

    repositories {
        val coreReleases = maven {
            url = uri("https://repox.jfrog.io/repox/sonarsource-releases")
            credentials {
                username = artifactoryUsername
                password = artifactoryPassword
            }
        }
        maven {
            url = uri("https://repox.jfrog.io/repox/sonarsource")
            credentials {
                username = artifactoryUsername
                password = artifactoryPassword
            }
        }
        exclusiveContent {
            forRepositories(coreReleases)
            filter {
                includeGroup("com.sonarsource.sonarcloud")
                includeGroup("com.sonarsource.sonarcloud.core")
            }
        }
    }
}

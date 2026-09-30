rootProject.name = "pysonar-sqc-it"

dependencyResolutionManagement {
    repositories {
        maven {
            url = uri("https://repox.jfrog.io/repox/sonarsource")
            credentials {
                username = System.getenv("ARTIFACTORY_USERNAME")
                    ?: providers.gradleProperty("artifactoryUsername").orNull.orEmpty()
                password = System.getenv("ARTIFACTORY_PASSWORD")
                    ?: providers.gradleProperty("artifactoryPassword").orNull.orEmpty()
            }
        }
    }
}

FROM --platform=linux/amd64 eclipse-temurin:17-jdk-jammy AS builder
WORKDIR /builder

COPY settings.gradle build.gradle ./
COPY src ./src

RUN apt update && apt upgrade -y && apt install zip unzip -y
RUN curl -L https://services.gradle.org/distributions/gradle-8.3-bin.zip -o "gradle.zip" \
    && unzip gradle.zip

ENV GRADLE_HOME=/builder/gradle-8.3

RUN export PATH=$PATH:$GRADLE_HOME/bin && gradle assemble

FROM eclipse-temurin:17-jre-jammy

WORKDIR /app
COPY --from=builder /builder/build/libs/msk-gsr-spring-kafka-producer-0.0.1.jar /app/app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "/app/app.jar"]

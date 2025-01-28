FROM amazon/aws-cli:2.17.64 AS awscli-installer

FROM amazoncorretto:21.0.5-al2023 AS builder
WORKDIR /opt/app

COPY src src
COPY pom.xml pom.xml
COPY mvnw mvnw
COPY .mvn .mvn

RUN chmod +x mvnw && ./mvnw clean package -DskipTests --no-transfer-progress

FROM amazoncorretto:21.0.5-al2023-headless AS runtime

COPY src src
COPY pom.xml pom.xml
COPY mvnw mvnw
COPY .mvn .mvn

RUN chmod +x mvnw && ./mvnw clean package -DskipTests --no-transfer-progress

WORKDIR /opt/app

COPY --from=awscli-installer /usr/local/bin /usr/local/bin
COPY --from=awscli-installer /usr/local/aws-cli/ /usr/local/aws-cli/

COPY --from=builder /opt/app/target/cloud-runtime-api.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
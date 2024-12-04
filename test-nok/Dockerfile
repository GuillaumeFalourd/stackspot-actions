# Etapa 1: Usar a imagem oficial do AWS CLI para obter o binário
FROM amazon/aws-cli:2.17.64 AS awscli-installer

FROM amazoncorretto:22.0.2-al2023 AS builder
WORKDIR /opt/app

# Copiar os arquivos da aplicação
COPY src src
COPY pom.xml pom.xml
COPY mvnw mvnw
COPY .mvn .mvn

# Compilar a aplicação
RUN chmod +x mvnw && ./mvnw clean package -DskipTests --no-transfer-progress

# Etapa 2: Usar a imagem amazoncorretto para o runtime
FROM amazoncorretto:23.0.1-al2023 AS runtime
#Copiar os arquivos da aplicação
COPY src src
COPY pom.xml pom.xml
COPY mvnw mvnw
COPY .mvn .mvn

# Compilar a aplicação
RUN chmod +x mvnw && ./mvnw clean package -DskipTests --no-transfer-progress

# Definir o diretório de trabalho
WORKDIR /opt/app

# Copiar o AWS CLI da etapa anterior
COPY --from=awscli-installer /usr/local/bin /usr/local/bin
COPY --from=awscli-installer /usr/local/aws-cli/ /usr/local/aws-cli/
#COPY --from=awscli-installer /usr/local/bin/aws /usr/local/bin/aws

# Copiar o jar da aplicação da etapa de build
COPY --from=builder /opt/app/target/cloud-runtime-api.jar app.jar

# Expor a porta 8080
EXPOSE 8080

# Comando de entrada para rodar a aplicação
ENTRYPOINT ["java", "-jar", "app.jar"]

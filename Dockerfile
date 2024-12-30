# 1단계: 빌드 환경 설정 (Gradle 사용)
# Gradle 8.11.1과 Java 17이 설치된 이미지를 기반으로 시작
FROM gradle:8.11.1-jdk17 AS build

# 작업 디렉터리 설정: 컨테이너 내에서 코드를 저장하고 실행할 위치 지정
WORKDIR /app

# Gradle 빌드 도구 및 설정 파일 복사
# - build.gradle: 프로젝트의 빌드 설정을 정의
# - settings.gradle: 프로젝트 구성 및 종속성 관리 설정
# - gradlew: Gradle을 실행할 수 있는 스크립트 파일
COPY build.gradle settings.gradle gradlew /app/  

# Gradle 관련 폴더 복사 (의존성 관리 도구 포함)
COPY gradle /app/gradle

# 소스 코드 복사
# - src 폴더에는 실제 프로그램 코드가 저장됨
COPY src /app/src

# 실행 권한 부여
# - gradlew 파일에 실행 권한을 추가하여 실행 가능하도록 설정
RUN chmod +x ./gradlew

# Gradle을 이용하여 프로젝트 빌드
# - clean: 기존 빌드 결과 삭제
# - build: 프로젝트 컴파일 및 패키징
# - --no-daemon: 백그라운드 프로세스를 사용하지 않고 실행
RUN ./gradlew clean build --no-daemon

# 2단계: 실행 환경 설정 (Java 실행 환경)
# 경량화된 OpenJDK 17 이미지를 사용하여 최종 실행 환경 구축
FROM openjdk:17-jdk-slim

# 작업 디렉터리 설정
WORKDIR /app

# 빌드 결과물 복사
# - 이전 단계(build)에서 생성된 jar 파일을 실행 환경으로 복사
COPY --from=build /app/build/libs/ /app/

# 최종 빌드된 .war 파일 복사
# - *SNAPSHOT.war 파일을 실행할 주 파일로 지정
COPY --from=build /app/build/libs/*SNAPSHOT.war /app/app.war

# .war 파일 실행 명령 설정
# - Java 명령어로 실행하며, -jar 옵션을 통해 지정된 .war 파일 실행
ENTRYPOINT ["java", "-jar", "/app/app.war"]
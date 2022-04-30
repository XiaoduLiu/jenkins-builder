FROM alpine:3.7
ARG user=jenkins
ARG group=jenkins
ARG uid=10000
ARG gid=10000
ARG USER_HOME_DIR=/home/${user}
ENV JENKINS_AGENT_HOME ${USER_HOME_DIR}
RUN addgroup -g ${gid} ${group}
RUN adduser -h "${JENKINS_AGENT_HOME}" -u "${gid}" -G "${user}" -s /bin/ash "${user}" -D
RUN apk --update add postgresql-client && rm -rf /var/cache/apk/*

#!/usr/bin/expect -f

set timeout -1
set ccloud_email [lindex $argv 0]
set ccloud_password [lindex $argv 1]
spawn ccloud login --url https://confluent.cloud
expect "Email:"
send -- "$ccloud_email\r"
expect "Password:"
send -- "$ccloud_password\r"
expect eof

#!/bin/bash
SERVER=$1
`cat /Users/clin/.ssh/id_rsa.pub | ssh $SERVER 'cat >> .ssh/authorized_keys'`

ansible-playbook -i inventory/apache_server_list.ini Apache_WL_App_All_steps.yml  -u touser --become --extra-vars "appname_i=ARISInter env_dtup=DEV webservers=webservers_Inter remote_port=22"


![[MIT License](https://img.shields.io/bower/l/MI?style=flat-square)](https://img.shields.io/bower/l/MI?style=for-the-badge)

# About The Project
This repository contains the project of my final degree work, carried out at the [Escuela Superior de Informática](https://esi.uclm.es/) de Ciudad Real, [University of Castilla-La Mancha.](https://www.uclm.es/).

This project implements a technological architecture that supports the P4 medicine paradigm, covering all the layers, from data collection to storage and subsequent processing in the electronic record of the
and subsequent processing in the electronic record of an individual, using [FHIR](https://hl7.org/fhir/) technology to handle this information.

## Built with
This project has been developed using the following languages and tools:

* <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/Python_logo_and_wordmark.svg/1280px-Python_logo_and_wordmark.svg.png" width="100">
* <img src="https://lanpixel.com/wp-content/uploads/2021/09/Logo-Docker.png" width="100">
* <img src="https://www.turnkeylinux.org/files/images/postgresql-logo-for-blog.png" width="100">
* <img src="https://miro.medium.com/v2/resize:fit:1400/1*4M4OghuybPhjRsLxhrNsGA.png" width="100">
* <img src="https://s4-recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/logos/400/626/900/original/ngrok-blue-lrg.png?1635367310" width="80">

# Getting Started
## Prerequisites 
This project has been developed and tested on the following versions of the previously mentioned technologies:

| Technology  | Version  |
|-------------|----------|
| Python      | 3.10.6   |
| Docker      | 23.03    |
| PostgreSQL  | 14.8     |
| Grafana     | 9.5.2    |
| Ngrok       | 3.2.2    |
| Ubuntu      | 22.04.2  |
|

In addition, you will need a Withings device (in this case the Withings Body Cardio Scale has been used), a developer account at [Withings](https://developer.withings.com/). Here you will need to create an app on the dashboard, where you will be given a set of credentials for your app, a client-id and a client-secret, as it uses OAuth2 authentication.

## Instalation

1. You must clone this repository into a directory of your choice and work from there.
    ```sh
    git clone https://github.com/JASantacruz/TFG.git
    ```
2. (Optional) Create a virtual environment in python
    ```sh
    python3 -m venv env
    ```
3. (Only if you have performed step 2). Activate the    virtual environment
    ```sh
    source env/bin/activate    
    ```
4. Install the required Python packages
   ```sh
   pip install -r requirements.txt
   ```
5. Download the Docker FHIR server from [LinuxForHealth](https://github.com/LinuxForHealth/FHIR) and follow these [configuration steps](https://github.com/LinuxForHealth/FHIR/tree/main/fhir-persistence-schema) to make the connection to the database.
   Here is a brief summary:
   1. We create the Docker container from the image provided by LinuxForHealth
        ```sh
        docker run -p 9443:9443 -e BOOTSTRAP_DB=false ghcr.io/linuxforhealth/fhir-server
        ```

        We set the flag BOOTSTRAP_DB=false, because if we set this flag to true the Apache Derby database will be installed, and we will use PostgreSQL

        When the server is running, we check that it is running correctly by accessing the following URLs

        * https://localhost:9443/fhir-server/api/v4/metadata     Should return the server metada
        * https://localhost:9443/fhir-server/api/v4/$healthcheck
        You should ask us for credentials. By default they are:
          - Username: fhiruser
          - Password: change-password

        We should receive a FHIRPersistenceDBConnectException error. This is expected, since when installing the server we established that we did not want the Apache Derby database, since we will be working with PostgreSQL.

    2. At this point, the FHIR server is up and running. Now we will have to install the PostgreSQL database
        ```sh
        sudo apt install postgresql postgresql-contrib
        ```

        After this, we have the PostgreSQL server up and running. By default, this server only listens on the localhost interface, and only supports connections from there, so we will have to make changes in the configuration files.

        To do this, we need to know the interface through which it will receive the requests, that is, the IP address of the Docker container. 

        1. Identify the container ID with ```docker ps```
        2. We open a shell as superuser in the container with ```docker exec -it -u 0 <container_id> /bin/bash```
        3. To know the IP address, we can use the ```ip addr``` command, which is not installed. The docker container uses a RedHat image, so we must execute the following command ```yum install iproute```
        4. We answer with "y" to the question asked by the installer. Once we have it installed, we run the command ```ip addr``` and we see that the IP assigned to the interface in the profile eth0. In my case, 172.17.0.2

            On our machine, we also check that there is a docker0 interface, with an IP on the same network. In my case 172.17.0.1

        5. Now we proceed with the configuration of the PostgreSQL server, which we will update to allow us to make connections from the container. 

            We will go to the /etc/postgresql/<version>/main/pg_hba.conf file.

            First, we need to open connections from the host <ip profile docker0 of our machine>, user fhirserver and database fhirdb. Add the following two lines
        
            ```sh
            # TYPE  DATABASE        USER            ADDRESS                 METHOD
            hostssl fhirdb          fhirserver      172.17.0.1/32           md5

            # "local" is for Unix domain socket connections only
            host    all             all             172.17.0.2/32           trust
            ```
        6. The next PostgreSQL configuration file to be updated is /etc/postgresql/<version>/main/postgresql.conf.
        In this file, we must find the commented line starting with ```listen_addresses``` and set the following value:

            ```sh
            listen_addresses = 'localhost,172.17.0.1' # what IP address(es) to listen on;
            ```

        7. Now, we will create the user and the database using psql.
            ```psql -U postgres -h localhost -d fhirdb```
        When we get the >postgres=# prompt, we execute the following commands
            ```sql
                >postgres=# create database fhirdb;
                >postgres=# create user fhirserver with password 'change-password';
            ```

        8. Once this is done, we will install the FHIR scheme. To do this we use the script and the steps to follow from the following [link](https://github.com/LinuxForHealth/FHIR/tree/main/fhir-persistence-schema)

            We clone the repository, and create a properties file named ```fhirdb.properties``` with the following structure
            ```properties
            db.host=localhost
            db.port=5432
            db.database=fhirdb
            user=postgres
            password=change-password
            ```

        9.  Once the file has been downloaded, and the properties file has been created, we execute the commands indicated by LinuxForHealth

            To create the schemas
            ```sh
            java -jar ./fhir-persistence-schema-5.1.1-cli.jar \
            --db-type postgresql
            --prop-file fhirdb.properties \
            --schema-name fhirdata
            --create-schemas
            ```

            To update the schemas and link them to the fhirserver user
                
            ```sh
            java -jar ./fhir-persistence-schema-5.1.1-cli.jar \
            --db-type postgresql
            --prop-file fhirdb.properties \
            --schema-name fhirdata \
            --update-schema
            --grant-to fhirserver
            --pool-size 1
            ```

            To check that this has been executed correctly, in the terminal where we had opened the shell with psql, we can execute the command ```dn``` and see the schemas created.

        10. Next, we configure the datasource on the FHIR server, following these [instructions](https://linuxforhealth.github.io/FHIR/guides/FHIRServerUsersGuide/#33-persistence-layer-configuration)


            1. First, on the docker server, we will need a text editor, for example, ```nano```.

                ```sh
                yum install nano
                ```
            2. Now, following the guide mentioned above, we will configure the data source in the configDropins directory.

                ```sh
                cd configDropins
                ```

                In this directory we will find 3 folders
                * default
                * overrides
                * disabled

                we will focus mainly on the last two.

                In the disabled directory, we will find a configuration file example for the PostgreSQL database, it will be the one we will use. We will copy this file to the overrides directory

                ```
                cp disabled/datasource-postgresql.xml ./overrides
                ```

            3. Once we have copied this file to overrides, we edit with nano to change the ```serverName``` field.

                ```sh
                nano datasource-postgresql.xml
                ```

                In the ````serverName``` field we will set the IP address that we had in the docker0 interface, in my case 172.17.0.1
                ```
                serverName="172.17.0.1"
                ```

            4. Next, we edit the other configuration file, which is located in the path config/default/fhir-server-config.json

                ```sh
                nano config/default/fhir-server-config.json
                ```

                And we look for the "persistence" property, edit it, and set the following values for it, leaving the rest of the file with its default values

                ```json
                "persistence": {
                            "factoryClassname": "org.linuxforhealth.fhir.persistence.jdbc.FHIRPersistenceJDBCFactory$
                            "common": {
                                "__comment": "Configuration properties common to all persistence layer implementatio$ "__comment": "configuration properties common to all persistence layer implementatio$
                                "updateCreateEnabled": true
                            },
                            "jdbc": {
                                "__comment": "Configuration properties for the JDBC persistence implementation",
                                "enableCodeSystemsCache": true,
                                "enableParameterNamesCache": true,
                                "enableResourceTypesCache": true.
                            },
                            "datasources": {
                                "default": {
                                    "jndiName": "jdbc/fhir_default_default",
                                    "type": "postgresql",
                                    "currentSchema": "fhirdata".
                                },

                ```
            5. Finally, we restart the docker container, and the postgresql services using the following commands

                ```sh
                docker restart <container_id>
                sudo systemctl restart postgresql@14-main.service
                sudo systemctl restart postgresql.service
                ```

            Now, if we go back to the $healthcheck path, where we saw the FHIRPersistenceDBConnectException error before, it should now show us a blank page, with no errors. We can use the ```curl``` command to create a patient, and test our system.

            ```sh
            curl -k -u fhiruser:change-password -X POST -H "Content-Type: "application/json" -d '{"resourceType": "Patient", "name": [{"given": ["John"], "family": "Doe"}]}' https://localhost:9443/fhir-server/api/v4/Patient
            ```

            And we can check if it has been created correctly from ```https://localhost:9443/fhir-server/api/v4/Patient```.

    

6. Once we have all this in place, we will install [ngrok](https://ngrok.com/). 
 
    For the development of this system, an ngrok license has been used, which allows to always establish the same subdomain. Without this functionality, we would be forced to always change the CALLBACK_URI in our Withings application.

7. Create an environment variable file .env with the following structure
    ```sh
    WITHINGS_CLIENT_ID=<your Withings client-id>
    WITHINGS_CLIENT_SECRET=<your Withings client-secret>
    CALLBACK_URL=<ngrok callback url>
    POST_MEHOD="POST"
    GET_METHOD="GET"
    FHIR_USER=<username set in Docker>
    PASSWORD=<password set in Docker>
    PATIENT_ENDPOINT=<docker fhir url for patients>
    OBSERVATION_ENDPOINT="<docker fhir url for observations>"
    ACCOUNT_WITHINGS_URL="https://account.withings.com"
    URL_FILE="./url.tmp"
    ``` 

8. Run the ```setup.sh``` script, where the ```Flask``` and ```Ngrok``` server will be started. After that, we only need to launch the ```main.py``` file and we will have our application running.

    Now, we can create Patients and Observations for those patients. 

9. Finally, we will implement [Grafana](https://grafana.com/) with our project.

    Download Grafana self-manager from the official website. 
    Once you have Grafana running, access the URL

    ```localhost:3000```.

    We will have to establish a new data source, of PostgreSQL type, with port, user and password established.

    Now, we must create a new Dashboard, in which we will create a new panel, which will be of type Time Series, and we will set the following query
    
    ```sql
    select distinct oqv.quantity_value as "Measure", odv.date_start as Date from fhirdata.observation_quantity_values oqv, fhirdata.observation_date_values odv
        where oqv.logical_resource_id = odv.logical_resource_id
        group by odv.logical_resource_id , oqv.quantity_value, odv.date_start
        order by odv.date_start;
    ```

# Usage

This project is mainly focused on those people who live in towns where there are no medical centres, and have to move to another city with these resources, which is very common in Spain. The ultimate goal of this project is to develop a closer and more personalised healthcare system for people with this type of problem, thus solving the need for them to travel, but it can also be used at an individual level, where it is enough for a user to have a Withings device to use this system.

## License

Distributed under the MIT License. See LICENSE.txt for more information.

## Contact

José Antonio Santacruz Gallego - joseantonio.santacruz00@gmail.com

## Acknowledgments

* [Public Withings API integration guide](https://developer.withings.com/developer-guide/v3/integration-guide/public-health-data-api/public-health-data-api-overview/)
* [HL7 FHIR](http://hl7.org/fhir/)
* [LinuxForHealth FHIR Server User's Guide](https://linuxforhealth.github.io/FHIR/guides/FHIRServerUsersGuide/)
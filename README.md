[![Build Status](https://travis-ci.org/bomdiabot/memedata-service.svg?branch=dev)](https://travis-ci.org/bomdiabot/memedata-service)

                                              ___,___,_______,____
                                             |  :::|///./||'||    \
                                             |  :::|//.//|| || M)  |
                                             |  :::|/.///|!!!|     |
                                             |   _______________   |
                                             |  |:::::::::::::::|  |
                                             |  |_______________|  |
                                             |  |_______________|  |
                                             |  |_______________|  |
                                             |  |_______________|  |
                                             ||_|               ||_|
                                             |__|_______________|__|

                                                           _             _                      
                        _ __     ___    _ __     ___    __| |   __ _    | |_    __ _      o O O 
                       | '  \   / -_)  | '  \   / -_)  / _` |  / _` |   |  _|  / _` |    o      
                       |_|_|_|  \___|  |_|_|_|  \___|  \__,_|  \__,_|   _\__|  \__,_|   TS__[O] 
                    _  |"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""| {======| 
                      "`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'./o--000' 


# Memedata Service
This service implements the images/texts/memes access service for bomdiabot system.

## Installing, Running and Testing
### Via Docker
- Install docker and docker-compose.
- Download the repo.
- In the repo root dir, run:
`docker install -t memedata .`
- Edit the `docker-compose.yml` files to correctly map your local `volumes` to the dev/prod container volumes.
- Build: `docker-compose build`
- Build the prod database: `docker-compose run memedata_api ./init_db.sh <SUPERUSER_PASSWORD>`
- Run the server: `docker-compose up`

**Testing**:

- Run the tests: `docker-compose run memedata_api ./run_tests.sh`

**Dev server**:

- Build the dev database: `docker-compose run memedata_api bash -c "$(./ch_dev_env.sh); ./init_db.sh <SUPERUSER_PASSWORD>"`
- Populate the dev database with random data: `docker-compose run memedata_api bash -c "$(./ch_dev_env.sh); ./init_db.sh <SUPERUSER_PASSWORD>"`
- Run the dev server: `docker-compose run memedata_api bash -c "$(./ch_dev_env.sh); ./run_server.sh"`

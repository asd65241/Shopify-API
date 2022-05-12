# Shopify API

This API used to interact with the Shopify backend.

## Current Features

- This API support custom login
- This API support retriveing sales of n-day before today
- This API support retriveing sales of a particular date

## Run using Docker

Build the image using:
```bash
$ docker build -t shopify-api . 
```

Run the image using:
```
$ sudo docker run -d --name hktv-api -p 8000:80 shopify-api

```

Then, go to http://127.0.0.1:8000 to see the documentation of the API

## Using Docker Compose

Create a 'docker-compose.yml'
```bash
$ touch docker-compose.yml
```

Fill the 'docker-compose.yml' with the following template
```
services:
  shopify-api:
      build: .
      image: "shopify-api"
      container_name: "shopify-api"
      restart: "always"
      networks: 
          - "net"
      environment:
            VIRTUAL_HOST: "YOUR-DOMAIN"
            LETSENCRYPT_HOST: "YOUR-DOMAIN"
            VIRTUAL_PORT: "80"
          
networks:
    net:
        external: true
```

Then, do the following command:
```bash
$ sudo docker-compose up -d 
```

This will copy your environment variable to the container.

## Development

It is suggested to use pipenv to initialize your dev environment

```bash
$ pipenv shell
```

Then, run server by
```bash
$ bash run-server.sh
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
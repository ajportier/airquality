/*
PORTIONS ADAPTED FROM SUNFOUNDER LABS CODE EXAMPLE
http://www.sunfounder.com/

1. sudo apt-get install libcurl4-openssl-dev
2. sudo apt-get install libconfig-dev
3. git clone git://git.drogon.net/wiringPi
4. cd wiringPi
5. git pull origin
6. cd wiringPi
7. ./build
8. gcc sender.c -lwiringPi -lcurl -lconfig -o sender
*/

#include <stdio.h>
#include <stdlib.h>
#include <wiringPi.h>
#include <libconfig.h>
#include <curl/curl.h>

typedef unsigned char uchar;
typedef unsigned int  uint;

#define     ADC_CS    0
#define     ADC_CLK   1
#define     ADC_DIO   2

uchar get_ADC_Result(void)
{
	//10:CH0
	//11:CH1
	uchar i;
	uchar dat1=0, dat2=0;

	digitalWrite(ADC_CS, 0);

	digitalWrite(ADC_CLK,0);
	digitalWrite(ADC_DIO,1);	delayMicroseconds(2);
	digitalWrite(ADC_CLK,1);	delayMicroseconds(2);
	digitalWrite(ADC_CLK,0);

	digitalWrite(ADC_DIO,1);    delayMicroseconds(2); //CH0 10
	digitalWrite(ADC_CLK,1);	delayMicroseconds(2);
	digitalWrite(ADC_CLK,0);

	digitalWrite(ADC_DIO,0);	delayMicroseconds(2); //CH0 0
	
	digitalWrite(ADC_CLK,1);	
	digitalWrite(ADC_DIO,1);    delayMicroseconds(2);
	digitalWrite(ADC_CLK,0);	
	digitalWrite(ADC_DIO,1);    delayMicroseconds(2);
	
	for(i=0;i<8;i++)
	{
		digitalWrite(ADC_CLK,1);	delayMicroseconds(2);
		digitalWrite(ADC_CLK,0);    delayMicroseconds(2);

		pinMode(ADC_DIO, INPUT);
		dat1=dat1<<1 | digitalRead(ADC_DIO);
	}
	
	for(i=0;i<8;i++)
	{
		dat2 = dat2 | ((uchar)(digitalRead(ADC_DIO))<<i);
		digitalWrite(ADC_CLK,1); 	delayMicroseconds(2);
		digitalWrite(ADC_CLK,0);    delayMicroseconds(2);
	}

	digitalWrite(ADC_CS,1);

	pinMode(ADC_DIO, OUTPUT);
	
	return(dat1==dat2) ? dat1 : 0;
}

int main(void)
{
	uchar tmp;
    config_t cfg;
    config_setting_t *setting;
    const char *uri, *key;
    CURL *curl;
    CURLcode res;

    // Configuration Setup
    config_init(&cfg);

    if(! config_read_file(&cfg, "config.cfg")){
        fprintf(stderr, "%s:%d - %s\n", config_error_file(&cfg),
            config_error_line(&cfg), config_error_text(&cfg));
        config_destroy(&cfg);
        return(EXIT_FAILURE);
    }

    if(! config_lookup_string(&cfg, "uri", &uri)){
        fprintf(stderr, "No 'uri' setting in configuration\n");
        return(EXIT_FAILURE);
    }

    if(! config_lookup_string(&cfg, "key", &key)){
        fprintf(stderr, "No 'key' setting in configuration\n");
        return(EXIT_FAILURE);
    }

    // CURL Setup
    curl = curl_easy_init();
    if (! curl) {
        fprintf(stderr, "libcurl setup error\n");
        return(EXIT_FAILURE);
    }
    curl_easy_setopt(curl, CURLOPT_URL, uri);

    // GPIO Setup
	if(wiringPiSetup() == -1){
		printf("setup wiringPi failed !");
		return 1; 
	}

	pinMode(ADC_CS,  OUTPUT);
	pinMode(ADC_CLK, OUTPUT);

    // Main Loop
	while(1){
		pinMode(ADC_DIO, OUTPUT);
		tmp = get_ADC_Result();
		printf("%d\n",tmp);
        res = curl_easy_perform(curl);
        if (res != CURLE_OK){
            fprintf(stderr, "curl failed: %s\n",
                    curl_easy_strerror(res));
        }
        delay(1000);
	}

    curl_global_cleanup();
	return 0;
}

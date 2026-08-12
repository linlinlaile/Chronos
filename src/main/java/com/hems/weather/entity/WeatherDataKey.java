package com.hems.weather.entity;

import lombok.Data;

import java.io.Serializable;

@Data
    public class WeatherDataKey implements Serializable {
        private String date;
        private int timeScope;

        public WeatherDataKey() {
            super();
        }

        public WeatherDataKey(String data, int timeScope) {
            this.date = data;
            this.timeScope = timeScope;
        }
    }
package com.hems.weather.entity;

import lombok.Data;

import java.io.Serializable;

@Data
    public class WeatherInfoKey implements Serializable {
        private String date;
        private String time;
    }
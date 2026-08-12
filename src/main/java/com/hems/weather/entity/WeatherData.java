package com.hems.weather.entity;

import lombok.Data;

import javax.persistence.*;
import java.io.Serializable;

/**
 * @Auther: wll
 * @Date: 20-2-26 17:46
 * @Description:
 */
@Data
@Table(name = "weather_data")
@Entity
@IdClass(WeatherDataKey.class)
public class WeatherData {
    @Id
    @Column(name = "date")
    private String date;
    @Id
    @Column(name = "time_scope")
    private int timeScope;
    @Column(name = "temperature")
    private double temprature;
    @Column(name = "humidity")
    private double humidity;
    @Column(name = "hum_temprature")
    private double humTemprature;
    @Column(name = "wbgt")
    private double wbgt;
    @Column(name = "is_holiday")
    private boolean isHoliday;
}

package com.hems.weather.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.persistence.*;
import java.io.Serializable;

/**
 * @Auther: wll
 * @Date: 20-2-26 17:40
 * @Description:
 */
@Data
@IdClass(WeatherInfoKey.class)
@Entity
@Table(name = "weather_info")
public class WeatherInfo implements Comparable<WeatherInfo> {
    @Id
    @Column(name = "date")
    private String date;
    @Id
    @Column(name="time")
    private String time;
    @Column(name = "city")
    private String city;
    @Column(name="temperature")
    private int temperature;
    @Column(name = "humidity")
    private int humidity;
    @Column(name = "sky")
    private String sky;
    @Column(name = "hum_temperature")
    private int humTemperature;
    @Column(name = "wbgt")
    private double wbgt;
    @Column(name = "wind")
    private String wind;

    @Override
    public int compareTo(WeatherInfo w) {
        return this.time.compareTo(w.getTime());
    }


}

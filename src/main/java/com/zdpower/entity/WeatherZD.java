package com.zdpower.entity;

import lombok.Data;

import javax.persistence.*;
import java.io.Serializable;
import java.util.Date;

/**
 * @Auther: wll
 * @Date: 20-2-26 17:46
 * @Description:
 */
@Data
@Table(name = "weather_ZD")
@Entity
public class WeatherZD {
    @Id
    @Column(name = "id")
    private Long id;
    @Column(name = "city")
    private String city;
    @Column(name = "create_time")
    private Date createTime;
    @Column(name = "station_code")
    private String stationCode;
    @Column(name = "weather_date")
    private Date weatherDate;
    @Column(name = "week")
    private Integer week;
    @Column(name = "weather24")
    private String weather24;
    @Column(name = "night_weather24")
    private String nightWeather24;
    @Column(name = "temperature24")
    private String temperature24;
    @Column(name = "night_temperature24")
    private String nightTemperature24;
    @Column(name = "wind24")
    private String wind24;
    @Column(name = "night_wind24")
    private String nightWind24;
    @Column(name = "power24")
    private String  power24;
    @Column(name = "night_power24")
    private String nightPower24;
    @Column(name = "update_time")
    private Date updateTime;
    @Column(name = "localtion")
    private String localtion;
    @Column(name = "humidity")
    private Double humidity;
    @Column(name = "relative_humidity")
    private Double relativeHumidity;
}

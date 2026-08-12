package com.hems.weather.repository;

import com.hems.weather.entity.WeatherData;
import com.hems.weather.entity.WeatherDataKey;
import com.hems.weather.entity.WeatherInfo;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

/**
 * @Auther: wll
 * @Date: 20-2-27 15:04
 * @Description:
 */
@Repository
public interface WeatherDataRespository extends JpaRepository<WeatherData, WeatherDataKey> {
}

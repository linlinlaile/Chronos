package com.hems.weather.repository;

import com.hems.weather.entity.WeatherInfo;
import com.hems.weather.entity.WeatherInfoKey;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

/**
 * @Auther: wll
 * @Date: 20-2-27 15:04
 * @Description:
 */
@Repository
public interface WeatherInfoRespository extends JpaRepository<WeatherInfo, WeatherInfoKey> {
}

DELIMITER //
CREATE PROCEDURE CreateCraigslistSite (
  IN subdomain_param NVARCHAR(90),
  IN site_name_param NVARCHAR(90),
  IN site_url_param NVARCHAR(250),
  IN city_param NVARCHAR(90),
  IN state_code_param NVARCHAR(90),
  IN country_param NVARCHAR(90),
  IN latitude_param FLOAT(10,6),
  IN longitude_param FLOAT(10,6),
  IN areas_param JSON
) BEGIN
INSERT INTO
  CraigslistSites (
    subdomain,
    site_name,
    site_url,
    city,
    state_code,
    country,
    latitude,
    longitude,
    areas
  )
VALUES
  (
    subdomain_param,
    site_name_param,
    site_url_param,
    city_param,
    state_code_param,
    country_param,
    latitude_param, 
    longitude_param,
    areas_param
  ) ON DUPLICATE KEY
UPDATE
    site_name = site_name_param,
    site_url = site_url_param,
    city = city_param,
    state_code = state_code_param,
    country = country_param,
    latitude = latitude_param,
    longitude = longitude_param,
    last_updated_at = CURRENT_TIMESTAMP,
    areas = areas_param;
END //
DELIMITER //
CREATE PROCEDURE CreateCraigslistQuery (
  IN search_id_param INT,
  IN query_param NVARCHAR(250),
  IN interval_mins_param INT,
  IN site_id_param INT,
  IN area_param NVARCHAR(20),
  IN category_param NVARCHAR(20),
  IN search_titles_param BOOLEAN,
  IN require_image_param BOOLEAN,
  IN posted_today_param BOOLEAN
) BEGIN
INSERT INTO
  CraigslistQueries (
    search_id,
    query,
    interval_mins,
    site_id,
    area,
    category,
    search_titles,
    require_image,
    posted_today
  )
VALUES
  (
    search_id_param,
    query_param,
    interval_mins_param,
    site_id_param,
    area_param,
    category_param,
    search_titles_param,
    require_image_param,
    posted_today_param
  );
END //
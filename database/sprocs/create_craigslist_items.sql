DELIMITER //
CREATE PROCEDURE CreateCraigslistItem (
  IN item_name_param NVARCHAR(90),
  IN price_param INT,
  IN search_id_param VARCHAR(50),
  IN source_url_param NVARCHAR(250),
  IN source_id_param VARCHAR(50),
  IN posted_at_param DATETIME,
  IN is_deleted_param BOOLEAN,
  IN has_image_param BOOLEAN,
  IN last_updated_param DATETIME,
  IN repost_of_param NVARCHAR(255),
  IN item_location_param NVARCHAR(90)
) BEGIN
INSERT INTO
  CraigslistItems (
    item_name,
    price,
    search_id,
    source_url,
    source_id,
    posted_at,
    is_deleted,
    has_image,
    last_updated,
    repost_of,
    item_location
  )
VALUES
  (
    item_name_param,
    price_param,
    search_id_param,
    source_url_param,
    source_id_param,
    posted_at_param,
    is_deleted_param,
    has_image_param,
    last_updated_param,
    repost_of_param,
    item_location_param
  ) ON DUPLICATE KEY
UPDATE
  item_name = item_name_param,
  price = price_param,
  is_deleted = is_deleted_param,
  last_updated = last_updated_param,
  last_seen_at = CURRENT_TIMESTAMP();
END //

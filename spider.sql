CREATE TABLE `scrapy-spider`.`jobbole_article` (
  `url_object_id` VARCHAR(50) NOT NULL,
  `title` VARCHAR(200) NOT NULL,
  `url` VARCHAR(300) NOT NULL,
  `front_image_url` VARCHAR(300) NULL,
  `front_image_path` VARCHAR(200) NULL,
  `praise_nums` INT(11) NOT NULL DEFAULT 0,
  `comment_nums` INT(11) NOT NULL DEFAULT 0,
  `fav_nums` INT(11) NULL DEFAULT 0,
  `tags` VARCHAR(200) NULL,
  `content` LONGTEXT NOT NULL,
  `create_date` DATETIME NULL,
  PRIMARY KEY (`url_object_id`));
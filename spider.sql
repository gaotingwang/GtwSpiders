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

CREATE TABLE `scrapy-spider`.`zhihu_question` (
  `zhihu_id` BIGINT(20) NULL,
  `topics` VARCHAR(255) NULL,
  `url` VARCHAR(300) NULL,
  `title` VARCHAR(300) NULL,
  `content` LONGTEXT NULL,
  `answer_num` INT(11) NULL,
  `comments_num` INT(11) NULL,
  `watch_user_num` INT(11) NULL,
  `click_num` INT(11) NULL,
  `create_time` DATETIME NULL,
  `update_time` DATETIME NULL,
  `crawl_time` DATETIME NULL,
  `crawl_update_time` DATETIME NULL);

CREATE TABLE `scrapy-spider`.`zhihu_answer` (
  `zhihu_id` BIGINT(20) NULL,
  `url` VARCHAR(300) NULL,
  `question_id` BIGINT(20) NULL,
  `author_id` VARCHAR(100) NULL,
  `content` LONGTEXT NULL,
  `parise_num` INT(11) NULL,
  `comments_num` INT(11) NULL,
  `create_time` DATETIME NULL,
  `update_time` DATETIME NULL,
  `crawl_time` DATETIME NULL,
  `crawl_update_time` DATETIME NULL);
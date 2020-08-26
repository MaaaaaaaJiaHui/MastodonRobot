-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- 主机： 127.0.0.1:3306
-- 生成日期： 2020-08-23 10:00:38
-- 服务器版本： 5.7.31
-- PHP 版本： 7.3.21

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 数据库： `mastodon_bot`
--

-- --------------------------------------------------------

--
-- 表的结构 `school_info_schoolinfo`
--

DROP TABLE IF EXISTS `school_info_schoolinfo`;
CREATE TABLE IF NOT EXISTS `school_info_schoolinfo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `info_name` varchar(512) COLLATE utf8_bin NOT NULL,
  `info_value` varchar(1024) COLLATE utf8_bin NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `deleted_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

--
-- 转存表中的数据 `school_info_schoolinfo`
--

INSERT INTO `school_info_schoolinfo` (`id`, `info_name`, `info_value`, `created_at`, `updated_at`, `deleted_at`) VALUES
(4, 'school_newbie_info', 'https://www.baidu.com', '2020-07-26 12:29:23.000000', '2020-07-26 16:13:14.179961', NULL),
(2, 'school_official_website', 'https://www.google.com', '2020-07-26 12:28:27.000000', '2020-07-26 12:28:27.000000', NULL),
(3, 'school_contact_info', 'https://www.google.com', '2020-07-26 12:28:27.000000', '2020-07-26 12:28:27.000000', NULL),
(5, 'school_f_and_q', 'https://www.twitter.com', '2020-07-26 12:29:23.000000', '2020-07-26 16:13:28.118937', NULL);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

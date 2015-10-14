-- MySQL dump 10.13  Distrib 5.1.73, for debian-linux-gnu (i486)
--
-- Host: localhost    Database: dryermon
-- ------------------------------------------------------
-- Server version	5.1.73-0ubuntu0.10.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `dryermon`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `dryermon` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `dryermon`;

--
-- Table structure for table `cargas`
--

DROP TABLE IF EXISTS `cargas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cargas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idlectura` int(11) NOT NULL,
  `fecha` datetime NOT NULL,
  `formula` smallint(6) NOT NULL,
  `marca` char(20) NOT NULL,
  `po` char(20) NOT NULL,
  `corte` char(20) NOT NULL,
  `proceso` char(30) NOT NULL,
  `fase` char(10) NOT NULL,
  `cantidad` smallint(6) NOT NULL,
  `observaciones` char(90) NOT NULL,
  `usuario` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `esclavos`
--

DROP TABLE IF EXISTS `esclavos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `esclavos` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `esclavo` int(10) unsigned NOT NULL,
  `nombre` varchar(5) NOT NULL,
  `descripcion` varchar(45) NOT NULL,
  `version` int(10) unsigned NOT NULL,
  `habilitado` tinyint(3) unsigned NOT NULL,
  `x1` int(10) unsigned NOT NULL,
  `x2` int(10) unsigned NOT NULL,
  `y1` int(10) unsigned NOT NULL,
  `y2` int(10) unsigned NOT NULL,
  `temp1` tinyint(3) unsigned NOT NULL,
  `temp2` tinyint(3) unsigned NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `lecturas`
--

DROP TABLE IF EXISTS `lecturas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lecturas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` datetime DEFAULT NULL,
  `secadora` int(11) DEFAULT NULL,
  `temp1` int(11) DEFAULT NULL,
  `temp2` int(11) DEFAULT NULL,
  `formula` int(11) DEFAULT NULL,
  `display` char(90) DEFAULT NULL,
  `entrada1` tinyint(1) DEFAULT NULL,
  `entrada2` tinyint(1) DEFAULT NULL,
  `version` int(11) DEFAULT NULL,
  `idcarga` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `fecha` (`fecha`,`secadora`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario` char(20) NOT NULL,
  `terminal` char(20) NOT NULL,
  `version` char(19) NOT NULL,
  `fechacreacion` datetime NOT NULL,
  `fechalogin` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-03-27 16:46:48

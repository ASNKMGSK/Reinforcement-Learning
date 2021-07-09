-- --------------------------------------------------------
-- 호스트:                          172.30.37.10
-- 서버 버전:                        10.5.5-MariaDB - Source distribution
-- 서버 OS:                        Linux
-- HeidiSQL 버전:                  11.2.0.6213
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- TRD 데이터베이스 구조 내보내기
DROP DATABASE IF EXISTS `TRD`;
CREATE DATABASE IF NOT EXISTS `TRD` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `TRD`;

-- 테이블 TRD.STKBLNC 구조 내보내기
DROP TABLE IF EXISTS `STKBLNC`;
CREATE TABLE IF NOT EXISTS `STKBLNC` (
  `YMD` int(8) NOT NULL DEFAULT date_format(current_timestamp(),'%Y%m%d'),
  `ACC_NO` varchar(20) NOT NULL,
  `ITEM` varchar(12) NOT NULL,
  `ITEM_NM` varchar(100) DEFAULT NULL,
  `CON_QTY` int(11) DEFAULT 0,
  `CON_PRC` int(11) DEFAULT 0,
  `TD_QTY` int(11) DEFAULT 0,
  `YD_QTY` int(11) DEFAULT 0,
  `VAL_AMT` bigint(20) DEFAULT 0,
  `PL_AMT` int(11) DEFAULT NULL,
  `RTIME` timestamp(6) NOT NULL DEFAULT current_timestamp(6),
  PRIMARY KEY (`YMD`,`ACC_NO`,`ITEM`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.

-- 테이블 TRD.STKCON 구조 내보내기
DROP TABLE IF EXISTS `STKCON`;
CREATE TABLE IF NOT EXISTS `STKCON` (
  `YMD` int(8) DEFAULT date_format(current_timestamp(),'%Y%m%d'),
  `RTIME` timestamp(6) NOT NULL DEFAULT current_timestamp(6),
  `ACC_NO` varchar(20) DEFAULT NULL,
  `STRTGY_NO` varchar(5) DEFAULT NULL,
  `item` varchar(12) DEFAULT NULL,
  `ODR_NO` int(11) DEFAULT 0,
  `ORG_NO` int(11) DEFAULT 0,
  `con_qty` int(11) DEFAULT 0,
  `con_prc` int(11) DEFAULT 0,
  `odr_tp` varchar(2) DEFAULT NULL,
  `con_tp` varchar(2) DEFAULT NULL,
  `cncl_tp` varchar(2) DEFAULT NULL,
  `short_qty` int(11) DEFAULT NULL,
  `blnc_qty` int(11) DEFAULT NULL,
  `odr_qty` int(11) DEFAULT NULL,
  `odr_prc` int(11) DEFAULT NULL,
  `odr_nm` varchar(100) DEFAULT NULL,
  `con_nm` varchar(100) DEFAULT NULL,
  `acc_nm` varchar(100) DEFAULT NULL,
  `item_nm` varchar(100) DEFAULT NULL,
  `MTIME` timestamp(6) NOT NULL DEFAULT current_timestamp(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.

-- 테이블 TRD.STKCURT 구조 내보내기
DROP TABLE IF EXISTS `STKCURT`;
CREATE TABLE IF NOT EXISTS `STKCURT` (
  `YMD` int(8) DEFAULT date_format(current_timestamp(),'%Y%m%d'),
  `RTIME` timestamp(6) NOT NULL DEFAULT current_timestamp(6),
  `item` varchar(12) DEFAULT NULL,
  `exp_con_tp` int(11) DEFAULT 0,
  `diff` int(11) DEFAULT NULL,
  `open` int(11) DEFAULT NULL,
  `high` int(11) DEFAULT NULL,
  `low` int(11) DEFAULT NULL,
  `short_prc` int(11) DEFAULT NULL,
  `long_prc` int(11) DEFAULT NULL,
  `vol` bigint(20) DEFAULT NULL,
  `acc_vol` bigint(20) DEFAULT NULL,
  `amt` bigint(20) DEFAULT NULL,
  `odr_tp` varchar(1) DEFAULT NULL,
  `close` int(11) DEFAULT NULL,
  `prc_sign` varchar(1) DEFAULT NULL,
  `acc_short_qty` bigint(20) DEFAULT NULL,
  `acc_long_qty` bigint(20) DEFAULT NULL,
  `acc_short_ASK_qty` bigint(20) DEFAULT NULL,
  `acc_long_ASK_qty` bigint(20) DEFAULT NULL,
  `item_nm` varchar(100) DEFAULT NULL,
  `time` int(11) DEFAULT 0,
  `times` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.

-- 테이블 TRD.STKHISTPRC 구조 내보내기
DROP TABLE IF EXISTS `STKHISTPRC`;
CREATE TABLE IF NOT EXISTS `STKHISTPRC` (
  `YMD` varchar(8) DEFAULT date_format(current_timestamp(),'%Y%m%d'),
  `ITEM` varchar(12) DEFAULT NULL,
  `ITEM_NM` varchar(100) DEFAULT NULL,
  `OPEN` int(11) DEFAULT NULL,
  `HIGH` int(11) DEFAULT NULL,
  `LOW` int(11) DEFAULT NULL,
  `CLOSE` int(11) DEFAULT NULL,
  `ACC_VOL` bigint(20) DEFAULT NULL,
  `DIFF` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.

-- 테이블 TRD.STKODR 구조 내보내기
DROP TABLE IF EXISTS `STKODR`;
CREATE TABLE IF NOT EXISTS `STKODR` (
  `YMD` int(8) DEFAULT date_format(current_timestamp(),'%Y%m%d'),
  `RTIME` timestamp(6) NOT NULL DEFAULT current_timestamp(6),
  `ACC_NO` varchar(20) DEFAULT NULL,
  `STRTGY_NO` varchar(5) DEFAULT NULL,
  `ITEM` varchar(12) DEFAULT NULL,
  `ODR_NO` int(11) DEFAULT 0,
  `QTY` int(11) DEFAULT 0,
  `PRC` int(11) DEFAULT 0,
  `ODR_TP` varchar(2) DEFAULT NULL,
  `COND_TP` varchar(2) DEFAULT NULL,
  `ODR_TICK_TP` varchar(2) DEFAULT NULL,
  `CON_QTY` int(11) DEFAULT 0,
  `CON_PRC` int(11) DEFAULT 0,
  `MTIME` timestamp(6) NOT NULL DEFAULT current_timestamp(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.

-- 테이블 TRD.STKPRCD 구조 내보내기
DROP TABLE IF EXISTS `STKPRCD`;
CREATE TABLE IF NOT EXISTS `STKPRCD` (
  `YMD` varchar(8) DEFAULT date_format(current_timestamp(),'%Y%m%d'),
  `RTIME` timestamp(6) NOT NULL DEFAULT current_timestamp(6),
  `ITEM` varchar(12) DEFAULT NULL,
  `ITEM_NM` varchar(100) DEFAULT NULL,
  `CLOSE` float DEFAULT NULL,
  `BF_CLOSE` float DEFAULT NULL,
  `DIFF` float DEFAULT NULL,
  `OPEN` float DEFAULT NULL,
  `HIGH` float DEFAULT NULL,
  `LOW` float DEFAULT NULL,
  `ACC_VOL` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.

-- 테이블 TRD.STKSTRTGY 구조 내보내기
DROP TABLE IF EXISTS `STKSTRTGY`;
CREATE TABLE IF NOT EXISTS `STKSTRTGY` (
  `YMD` int(8) DEFAULT date_format(current_timestamp(),'%Y%m%d'),
  `SEQ` bigint(20) NOT NULL AUTO_INCREMENT,
  `STRTGY_NO` decimal(5,0) DEFAULT NULL,
  `ITEM` varchar(12) DEFAULT NULL,
  `ODR_TP` varchar(1) DEFAULT NULL,
  `ODR_NO` int(15) DEFAULT 0 COMMENT '주문접수후 업데이트',
  `QTY` int(15) DEFAULT 0,
  `PRC` int(15) DEFAULT 0,
  `AMT` bigint(15) DEFAULT 0,
  `EXEC_TP` varchar(1) DEFAULT 'N' COMMENT '주문실행여부 Y 실행',
  `RSLT_TP` varchar(1) DEFAULT 'N' COMMENT '주문에러여부',
  `CON_TP` varchar(1) DEFAULT 'N' COMMENT '체결여부',
  `CAN_TP` varchar(1) DEFAULT 'N' COMMENT '취소여부',
  `MTIME` timestamp(6) NOT NULL DEFAULT current_timestamp(6),
  `MSG` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`SEQ`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.

-- 테이블 TRD.STKTICK 구조 내보내기
DROP TABLE IF EXISTS `STKTICK`;
CREATE TABLE IF NOT EXISTS `STKTICK` (
  `YMD` varchar(8) DEFAULT date_format(current_timestamp(),'%Y%m%d'),
  `SEQ` bigint(20) NOT NULL AUTO_INCREMENT,
  `RTIME` timestamp(6) NOT NULL DEFAULT current_timestamp(6),
  `ITEM` varchar(12) DEFAULT NULL,
  `ITEM_NM` varchar(100) DEFAULT NULL,
  `TIME` int(11) DEFAULT 0,
  `ASK_VWAP` decimal(20,8) DEFAULT 0.00000000,
  `BID_VWAP` decimal(20,8) DEFAULT 0.00000000,
  `MID_VWAP` decimal(20,8) DEFAULT 0.00000000,
  `MID_PRC` decimal(20,8) DEFAULT 0.00000000,
  `PRC_DIFF` decimal(20,8) DEFAULT 0.00000000,
  `ACC_VOL` bigint(20) DEFAULT 0,
  `ASK_QTY10` int(11) DEFAULT 0,
  `ASK_PRC10` int(11) DEFAULT 0,
  `ASK_QTY9` int(11) DEFAULT 0,
  `ASK_PRC9` int(11) DEFAULT 0,
  `ASK_QTY8` int(11) DEFAULT 0,
  `ASK_PRC8` int(11) DEFAULT 0,
  `ASK_QTY7` int(11) DEFAULT 0,
  `ASK_PRC7` int(11) DEFAULT 0,
  `ASK_QTY6` int(11) DEFAULT 0,
  `ASK_PRC6` int(11) DEFAULT 0,
  `ASK_QTY5` int(11) DEFAULT 0,
  `ASK_PRC5` int(11) DEFAULT 0,
  `ASK_QTY4` int(11) DEFAULT 0,
  `ASK_PRC4` int(11) DEFAULT 0,
  `ASK_QTY3` int(11) DEFAULT 0,
  `ASK_PRC3` int(11) DEFAULT 0,
  `ASK_QTY2` int(11) DEFAULT 0,
  `ASK_PRC2` int(11) DEFAULT 0,
  `ASK_QTY1` int(11) DEFAULT 0,
  `ASK_PRC1` int(11) DEFAULT 0,
  `BID_QTY1` int(11) DEFAULT 0,
  `BID_PRC1` int(11) DEFAULT 0,
  `BID_QTY2` int(11) DEFAULT 0,
  `BID_PRC2` int(11) DEFAULT 0,
  `BID_QTY3` int(11) DEFAULT 0,
  `BID_PRC3` int(11) DEFAULT 0,
  `BID_QTY4` int(11) DEFAULT 0,
  `BID_PRC4` int(11) DEFAULT 0,
  `BID_QTY5` int(11) DEFAULT 0,
  `BID_PRC5` int(11) DEFAULT 0,
  `BID_QTY6` int(11) DEFAULT 0,
  `BID_PRC6` int(11) DEFAULT 0,
  `BID_QTY7` int(11) DEFAULT 0,
  `BID_PRC7` int(11) DEFAULT 0,
  `BID_QTY8` int(11) DEFAULT 0,
  `BID_PRC8` int(11) DEFAULT 0,
  `BID_QTY9` int(11) DEFAULT 0,
  `BID_PRC9` int(11) DEFAULT 0,
  `BID_QTY10` int(11) DEFAULT 0,
  `BID_PRC10` int(11) DEFAULT 0,
  `ASK_TOT_QTY` bigint(20) DEFAULT 0,
  `BID_TOT_QTY` bigint(20) DEFAULT 0,
  `EXTIME_ASK_TOT_QTY` bigint(20) DEFAULT 0,
  `EXTIME_BID_TOT_QTY` bigint(20) DEFAULT 0,
  PRIMARY KEY (`SEQ`)
) ENGINE=InnoDB AUTO_INCREMENT=7150 DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.

-- 테이블 TRD.TIVTT 구조 내보내기
DROP TABLE IF EXISTS `TIVTT`;
CREATE TABLE IF NOT EXISTS `TIVTT` (
  `YMD` varchar(8) DEFAULT date_format(current_timestamp(),'%Y%m%d'),
  `SEQ` bigint(20) NOT NULL AUTO_INCREMENT,
  `RTIME` timestamp(6) NOT NULL DEFAULT current_timestamp(6),
  `MKT_TP` char(1) DEFAULT NULL,
  `MKT_NM` varchar(50) DEFAULT NULL,
  `IVT_TP` int(11) DEFAULT NULL,
  `IVT_NM` varchar(50) DEFAULT NULL,
  `TIME` int(11) DEFAULT NULL,
  `ASK_QTY` bigint(20) DEFAULT NULL,
  `ASK_AMT` bigint(20) DEFAULT NULL,
  `BID_QTY` bigint(20) DEFAULT NULL,
  `BID_AMT` bigint(20) DEFAULT NULL,
  `NET_BID_QTY` bigint(20) DEFAULT NULL,
  `NET_BID_AMT` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`SEQ`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;

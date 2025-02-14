BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS  operation_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        timestamp TEXT,
        operation TEXT
    );
INSERT INTO "operation_history" VALUES(1,'tim','2024-05-06 16:01:21','Login');
INSERT INTO "operation_history" VALUES(2,'bibby','2024-05-06 16:03:20','Registration');
INSERT INTO "operation_history" VALUES(3,'bibby','2024-05-06 16:03:27','Login');
INSERT INTO "operation_history" VALUES(4,'tim','2024-05-06 16:03:45','Login');
INSERT INTO "operation_history" VALUES(5,'tim','2024-05-06 18:08:40','Login');
INSERT INTO "operation_history" VALUES(6,'tim','2024-05-06 18:08:43','User Removal: bib');
INSERT INTO "operation_history" VALUES(7,'bib','2024-05-06 18:08:52','Registration');
INSERT INTO "operation_history" VALUES(8,'tim','2024-05-06 18:08:52','User Addition: bib with role 1');
INSERT INTO "operation_history" VALUES(9,'bib','2024-05-06 18:09:23','Password Change');
INSERT INTO "operation_history" VALUES(10,'bib','2024-05-06 18:09:58','Login');
INSERT INTO "operation_history" VALUES(11,'bib','2024-05-06 18:11:11','Reservation: scooper from 2024-05-20 10:00:00 to 12:00:00 for bib');
INSERT INTO "operation_history" VALUES(12,'bib','2024-05-06 18:11:20','Listed reservations by date range: 2024-05-10 to 2024-05-25');
INSERT INTO "operation_history" VALUES(13,'customer1','2024-05-08 01:05:22','Login');
INSERT INTO "operation_history" VALUES(14,'customer1','2024-05-08 01:05:51','Reservation: scanner from 2024-05-16 12:00:00 to 13:00:00 for customer1');
INSERT INTO "operation_history" VALUES(15,'customer1','2024-05-08 02:26:15','Login');
INSERT INTO "operation_history" VALUES(16,'customer1','2024-05-08 02:26:42','Reservation: scooper from 2024-05-18 12:00:00 to 14:00:00 for customer1');
CREATE TABLE IF NOT EXISTS  reservations (
            serial_number INTEGER PRIMARY KEY AUTOINCREMENT,
            equipment_name text,
            start_date text,
            start_time text,
            end_date text,
            end_time text,
            total_cost text,
            down_payment real,  
            customer_name real,
            block_array text,
            refund_amount REAL,
            status text);
INSERT INTO "reservations" VALUES(785419883,'harvester','2024-05-23','10:00:00','2024-05-23','12:00:00','176000.0',44000.0,'customer1','0', 0.0, 'Active');
INSERT INTO "reservations" VALUES(785419884,'scanner','2024-05-24','14:00:00','2024-05-24','15:00:00','990.0',247.5,'customer2','1,2,3', 0.0, 'Active');
INSERT INTO "reservations" VALUES(785419885,'scooper','2024-05-15','10:00:00','2024-05-15','12:00:00','2000.0',1000.0,'customer1','0', 0.0, 'Active');
INSERT INTO "reservations" VALUES(785419887,'scooper','2024-05-18','12:00:00','2024-05-18','14:00:00','2000.0',1000.0,'customer1','0', 0.0, 'Active');
CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT NOT NULL DEFAULT 'customer'
        , salt BLOB);
INSERT INTO "users" VALUES(12,'customer1',X'D2BEED7BD12890960FE57D8B69064872528800D6187F91FBD5A987B4CB4F670B','customer',X'93D1D78022DC3BD60830F13F01BAB02D2FC0F85BA814C650F777DE0BA3D4C0E0');
INSERT INTO "users" VALUES(13,'customer2',X'64D0019248AC3CC3F776161C16B86117E2F12BFB471139ADF479F0BDA9537996','customer',X'60CD8D2320671EFD59032CB5129AF479F638CD87C71F1A70AEEF0FE8F9A39D15');
INSERT INTO "users" VALUES(14,'scheduler1',X'24F75C1A6F95823074815AB43F4CAD2CB1BDDD7F73CF9F07157CC6B65E89C239','scheduler',X'367FE270921698186215643DC1284BCDBA5769AA6B39327C205AFB1A8F9FBA86');
INSERT INTO "users" VALUES(15,'scheduler2',X'E9190D9C68F6BAE8CF99DC19B42CF1251EFCA09CBDEF854A0A7701F87CFADD12','scheduler',X'AE5AE551E77B13701C54F472C88EA2663765260ACA01A8A218AC7940AAAA8D18');
INSERT INTO "users" VALUES(16,'admin1',X'B4E332009DF77E89FA893B52738FC5B3EF43A48F05AA3F3B3A68E5CE1D4082FE','admin',X'342BC34EF106A63170A18AE5719EE184D2F6FDC0E5D633E7410AC87F1DE8AC9B');
INSERT INTO "users" VALUES(17,'admin2',X'F8B47B5D145308A1389F9BE1C0DEE3DF401E691D652CE3B977AD2654024A4B1B','admin',X'5105D3D5E2011D2BBEEFD44C4D2DFB38D9DF46E8DEFD01B480195AD52BD8481C');
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('users',17);
INSERT INTO "sqlite_sequence" VALUES('reservations',785419887);
INSERT INTO "sqlite_sequence" VALUES('operation_history',16);
COMMIT;

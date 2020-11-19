-- Database: proposupdb

-- DROP DATABASE proposupdb;

--CREATE DATABASE proposupdb
--    WITH 
--    OWNER = postgres
--    ENCODING = 'UTF8'
--    LC_COLLATE = 'en_US.utf8'
--    LC_CTYPE = 'en_US.utf8'
--    TABLESPACE = pg_default
--    CONNECTION LIMIT = -1;

-- Role: proyecto
-- DROP ROLE proyecto;

--CREATE ROLE proyecto WITH
--  LOGIN
--  NOSUPERUSER
--  INHERIT
--  NOCREATEDB
--  NOCREATEROLE
--  NOREPLICATION
--  ENCRYPTED PASSWORD 'md51b08fc8f64d03debcd0723979948b1d5';
--
--GRANT postgres TO proyecto;

-- Extension: pgcrypto

-- DROP EXTENSION pgcrypto;

CREATE EXTENSION pgcrypto
    SCHEMA public
    VERSION "1.3";

-- Extension: plpgsql

-- DROP EXTENSION plpgsql;

-- CREATE EXTENSION plpgsql
--     SCHEMA pg_catalog
--     VERSION "1.0";

-- Extension: "uuid-ossp"

-- DROP EXTENSION "uuid-ossp";

CREATE EXTENSION "uuid-ossp"
    SCHEMA public
    VERSION "1.1";


-- Table: public.Rubros

-- DROP TABLE public."Rubros";

CREATE TABLE public."Rubros"
(
    "RubroId" uuid NOT NULL DEFAULT uuid_generate_v4(),
    "Familia" text COLLATE pg_catalog."default" NOT NULL,
    "RubroNombre" text COLLATE pg_catalog."default" NOT NULL,
    "Fecha_ALTA" date NOT NULL  DEFAULT CURRENT_DATE,
    "Fecha_BAJA" date ,
    CONSTRAINT "RubroId_PK" PRIMARY KEY ("RubroId"),
    CONSTRAINT "Familia_Rubro" UNIQUE ("Familia", "RubroNombre")
)

TABLESPACE pg_default;

ALTER TABLE public."Rubros"
    OWNER to proyecto;

INSERT INTO public."Rubros"("Familia", "RubroNombre") VALUES ('VIVIENDA', 	'Alquiler')                    ;
INSERT INTO public."Rubros"("Familia", "RubroNombre") VALUES ('VIVIENDA', 	'Comprar')                     ;
INSERT INTO public."Rubros"("Familia", "RubroNombre") VALUES ('VIVIENDA', 	'Alquiler Temporario')         ;
INSERT INTO public."Rubros"("Familia", "RubroNombre") VALUES ('CONSTRUCCIÓN', 'Reparaciones en altura')  ;
INSERT INTO public."Rubros"("Familia", "RubroNombre") VALUES ('CONSTRUCCIÓN', 'Edificios')               ;
INSERT INTO public."Rubros"("Familia", "RubroNombre") VALUES ('CONSTRUCCIÓN', 'Reparación en Domicilios');



-- Table: public.Usuarios

-- DROP TABLE public."Usuarios";

CREATE TABLE public."Usuarios"
(
    "UsuarioId" uuid NOT NULL DEFAULT uuid_generate_v4(),
    "Mail" text COLLATE pg_catalog."default" NOT NULL,
    "Rol" character(1) COLLATE pg_catalog."default" NOT NULL,
    "Password" text COLLATE pg_catalog."default" NOT NULL,
    "FECHA_ALTA" date NOT NULL DEFAULT CURRENT_DATE,
    "FECHA_MODIFICACION" date,
    "FECHA_BAJA" date,
    "Fecha_Origen" date NOT NULL,
    "Sexo" character(1) COLLATE pg_catalog."default" NOT NULL,
    "DocumentoNumero" bigint NOT NULL,
    "Nombre" text COLLATE pg_catalog."default" NOT NULL,
    "Apellido" text COLLATE pg_catalog."default",
    "DocumentoTipo" character varying(4) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT "IdUsuario_PK" PRIMARY KEY ("UsuarioId"),
    CONSTRAINT "EMAIL_UK" UNIQUE ("Mail")
)

TABLESPACE pg_default;

ALTER TABLE public."Usuarios"
    OWNER to proyecto;

COMMENT ON CONSTRAINT "EMAIL_UK" ON public."Usuarios"
    IS 'El mail NO se puede repetir bajo ningun aspecto';

-- Table: public.Propuestas

-- DROP TABLE public."Propuestas";

CREATE TABLE public."Propuestas"
(
    "PropuestaId" uuid NOT NULL DEFAULT uuid_generate_v4(),
    "UsuarioIdCreador" uuid NOT NULL,
    "RubroId" uuid NOT NULL,
	"NombrePROP" text COLLATE pg_catalog."default" NOT NULL,
    "Dias" integer NOT NULL,
    "Monto" money NOT NULL,
    "Descripcion" text COLLATE pg_catalog."default" NOT NULL,
    "Fecha_ALTA" date NOT NULL DEFAULT CURRENT_DATE,
    "Fecha_BAJA" date,
    CONSTRAINT "PropuestaId_PK" PRIMARY KEY ("PropuestaID"),
    CONSTRAINT "RubroPropuesta_FK" FOREIGN KEY ("RubroId")
        REFERENCES public."Rubros" ("RubroId") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT "UsuarioID_FK" FOREIGN KEY ("UsuarioIdCreador")
        REFERENCES public."Usuarios" ("UsuarioId") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE public."Propuestas"
    OWNER to proyecto;

-- Table: public.EmpresaRubros

-- DROP TABLE public."EmpresaRubros";

CREATE TABLE public."EmpresaRubros"
(
    "RubroEmpresaId" uuid NOT NULL DEFAULT uuid_generate_v4(),
    "EmpresaId" uuid NOT NULL,
    "RubroId" uuid NOT NULL,
    CONSTRAINT "RubrosEmpresa_pkey" PRIMARY KEY ("RubroEmpresaId"),
    CONSTRAINT "Empresa-UsuarioId_FK" FOREIGN KEY ("EmpresaId")
        REFERENCES public."Usuarios" ("UsuarioId") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT "RubroID_FK" FOREIGN KEY ("RubroId")
        REFERENCES public."Rubros" ("RubroId") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE public."EmpresaRubros"
    OWNER to proyecto;
-- Table: public.PropuestaRespuestas

-- DROP TABLE public."PropuestaRespuestas";

CREATE TABLE public."PropuestaRespuestas"
(
    "PropuestaRtaId" uuid NOT NULL DEFAULT uuid_generate_v4(),
    "PropuestaId" uuid NOT NULL,
    "EmpresaId" uuid NOT NULL,
    "AceptaProp" boolean NOT NULL,
    "Fecha_MOVIMIENTO" date NOT NULL DEFAULT CURRENT_DATE,
    "MontoRespuesta" money,
    "Comentario" text COLLATE pg_catalog."default",
	"Vigencia" integer,
    CONSTRAINT "PropuestaRta_PK" PRIMARY KEY ("PropuestaRtaId"),
    CONSTRAINT "EmpresaId_FK" FOREIGN KEY ("EmpresaId")
        REFERENCES public."Usuarios" ("UsuarioId") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT "PropuestaId_FK" FOREIGN KEY ("PropuestaId")
        REFERENCES public."Propuestas" ("PropuestaID") MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE public."PropuestaRespuestas"
    OWNER to proyecto;

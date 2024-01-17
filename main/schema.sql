--
-- PostgreSQL database dump
--

-- Dumped from database version 13.6 (Ubuntu 13.6-1.pgdg20.04+1)
-- Dumped by pg_dump version 13.6 (Ubuntu 13.6-1.pgdg20.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: update_sys_updated(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_sys_updated() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.sys_updated = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_sys_updated() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: tide_genbo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tide_genbo (
    datetime timestamp without time zone NOT NULL,
    symbol character varying(4) NOT NULL,
    highlow smallint NOT NULL,
    level smallint,
    sys_updated timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.tide_genbo OWNER TO postgres;

--
-- Name: tide_mst_genbo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tide_mst_genbo (
    created_date character varying(8) NOT NULL,
    place_no smallint NOT NULL,
    symbol character varying(4) NOT NULL,
    name character varying(10) NOT NULL,
    location text,
    longitude_degrees smallint,
    longitude_minutes smallint,
    longitude_seconds smallint,
    latitude_degrees smallint,
    latitude_minutes smallint,
    latitude_seconds smallint,
    method character varying(10),
    above_dl_mm smallint,
    above_tp_mm smallint,
    datum_line_mm smallint,
    remarks text,
    sys_updated timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.tide_mst_genbo OWNER TO postgres;

--
-- Name: tide_mst_suisan; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tide_mst_suisan (
    created_date character varying(8) NOT NULL,
    place_no smallint NOT NULL,
    symbol character varying(4) NOT NULL,
    name character varying(10) NOT NULL,
    longitude_degrees smallint,
    longitude_minutes smallint,
    longitude_seconds smallint,
    latitude_degrees smallint,
    latitude_minutes smallint,
    latitude_seconds smallint,
    msl_above_st_min_mm smallint,
    msl_above_tp_mm smallint,
    st_min_above_tp_mm smallint,
    tide_m2_amp real,
    tide_m2_angle real,
    tide_s2_amp real,
    tide_s2_angle real,
    tide_k1_amp real,
    tide_k1_angle real,
    tide_o1_amp real,
    tide_o1_angle real,
    remarks text,
    sys_updated timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.tide_mst_suisan OWNER TO postgres;

--
-- Name: tide_suisan; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tide_suisan (
    datetime timestamp without time zone NOT NULL,
    symbol character varying(4) NOT NULL,
    highlow smallint NOT NULL,
    level smallint,
    sys_updated timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.tide_suisan OWNER TO postgres;

--
-- Name: tide_genbo tide_genbo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tide_genbo
    ADD CONSTRAINT tide_genbo_pkey PRIMARY KEY (datetime, symbol, highlow);


--
-- Name: tide_mst_genbo tide_mst_genbo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tide_mst_genbo
    ADD CONSTRAINT tide_mst_genbo_pkey PRIMARY KEY (created_date, symbol);


--
-- Name: tide_suisan tide_suisan_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tide_suisan
    ADD CONSTRAINT tide_suisan_pkey PRIMARY KEY (datetime, symbol, highlow);


--
-- Name: tide_mst_suisan ttide_mst_suisan_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tide_mst_suisan
    ADD CONSTRAINT ttide_mst_suisan_pkey PRIMARY KEY (created_date, symbol);


--
-- Name: tide_genbo trg_update_sys_tide_genbo_0; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_update_sys_tide_genbo_0 BEFORE UPDATE ON public.tide_genbo FOR EACH ROW EXECUTE FUNCTION public.update_sys_updated();


--
-- Name: tide_mst_genbo trg_update_sys_tide_mst_genbo_0; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_update_sys_tide_mst_genbo_0 BEFORE UPDATE ON public.tide_mst_genbo FOR EACH ROW EXECUTE FUNCTION public.update_sys_updated();


--
-- Name: tide_mst_suisan trg_update_sys_tide_mst_suisan_0; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_update_sys_tide_mst_suisan_0 BEFORE UPDATE ON public.tide_mst_suisan FOR EACH ROW EXECUTE FUNCTION public.update_sys_updated();


--
-- Name: tide_suisan trg_update_sys_tide_suisan_0; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_update_sys_tide_suisan_0 BEFORE UPDATE ON public.tide_suisan FOR EACH ROW EXECUTE FUNCTION public.update_sys_updated();


--
-- PostgreSQL database dump complete
--


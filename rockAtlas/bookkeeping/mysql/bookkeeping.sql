update atlas_exposures set pyephem_mjd = ROUND(mjd, 1) where pyephem_mjd is null;
CALL update_dophot_photometry();
CALL update_stats_exposure_processing();
CALL update_stats_objects();
CALL update_atlas_objects();

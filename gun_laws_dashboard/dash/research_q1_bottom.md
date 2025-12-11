A.  2 models built from the dataset:
    
    1.  Using these features:
        * year
        * state
        * deaths
        * law_strength_score
        * restrictive_laws 
        * permissive_laws 
        * total_law_changes                             
        * law_strength_change 
        * unique_law_classes

    2.  Using these features:
        *state 
        *strength_background_checks
        *strength_carrying_a_concealed_weapon_ccw
        *strength_castle_doctrine
        *strength_dealer_license
        *strength_firearm_sales_restrictions
        *strength_local_laws_preempted_by_state', 'strength_minimum_age','strength_prohibited_possessor       
        *strength_registration', 'strength_waiting_period', 'strength_firearm_removal_at_scene_of_domestic_violence
        *strength_firearms_in_college_university', 'strength_child_access_laws', 'strength_gun_trafficking
        *strength_open_carry', 'strength_required_reporting_of_lost_or_stolen_firearms
        *strength_safety_training_required', 'strength_untraceable_firearms', 'strength_permit_to_purchase
        *strength_firearms_in_k_12_educational_settings

    TARGET: rate

B.  Basic Multi-Linear Modeling

    Data >> train/test split >> ColumnTransformer(OneHotEncoder()) >> Pipeline(transforms, LinearRegression())

C.  Ridge Regression

    Data >> train/test split >> ColumnTransformer(StandardScaler(), OneHotEncoder()) >> Pipeline(transforms, RidgeCV())

D.  Principal Component Analysis >> Multi-Linear Model

    Data >> train/test split
    * center training data
    * variance-covariance matrix
    * eigendecomposition >> eigenvalues, eigenvectors
    * SORT eigenvalues and eigenvectors (use order of values to sort vectors in the same order)
    * isolate top 4 eigenvectors
    * project training data on eigenvectors
    * center test data with the training data mean
    * project test data on eigenvectors
    * LinearRegression() >> .fit(training_data) >> .predict(test_data)

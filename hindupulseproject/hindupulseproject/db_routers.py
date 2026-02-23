

# class RegisterRouter:
#     """
#     A router to control all database operations on models in the
#     Production, Login, and Staging databases.
#     """

#     def db_for_read(self, model, **hints):
#         """Directs read operations to the appropriate database."""
#         if model.__name__ == 'Register':
#             return 'user_db'
#         if model.__name__ == 'StagingModel':  # Replace with your actual model name for the staging database
#             return 'staging_db'
     
#         return 'default'

#     def db_for_write(self, model, **hints):
#         """Directs write operations to the appropriate database."""
#         if model.__name__ == 'Register':
#             return 'user_db'
#         if model.__name__ == 'StagingModel':  # Replace with your actual model name for the staging database
#             return 'staging_db'
     
#         return 'default'

#     def allow_relation(self, obj1, obj2, **hints):
#         """Allows relations if models are in the same database."""
#         if obj1.__class__.__name__ == 'Register' or obj2.__class__.__name__ == 'Register':
#             return True
#         if obj1.__class__.__name__ == 'StagingModel' or obj2.__class__.__name__ == 'StagingModel':
#             return True
       
#         return None

#     def allow_migrate(self, db, app_label, model_name=None, **hints):
#         """Controls where migrations are allowed based on model name."""
#         if model_name == 'register':
#             return db == 'user_db'
#         if model_name == 'stagingmodel':
#             return db == 'staging_db'
        
#         return db == 'default'




class RegisterRouter:
    """
    A router to control all database operations on models in the
    Production, Login, and Staging databases.
    """

    def db_for_read(self, model, **hints):
        if model.__name__ == 'Register':
            return 'user_db'
        if model.__name__ in ['StagingModel', 'StagingMovieDetails']:
            return 'staging_db'
        return 'default'

    def db_for_write(self, model, **hints):
        if model.__name__ == 'Register':
            return 'user_db'
        if model.__name__ in ['StagingModel', 'StagingMovieDetails']:
            return 'staging_db'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        if obj1.__class__.__name__ == 'Register' or obj2.__class__.__name__ == 'Register':
            return True
        if obj1.__class__.__name__ in ['StagingModel', 'StagingMovieDetails'] or \
           obj2.__class__.__name__ in ['StagingModel', 'StagingMovieDetails']:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if model_name == 'register':
            return db == 'user_db'
        if model_name in ['stagingmodel', 'stagingmoviedetails']:
            return db == 'staging_db'
        return db == 'default'

var app = angular.module('monitorrent', ['ngMaterial', 'ngRoute', 'ngSanitize', 'ngMessages']);

app.config(function ($httpProvider, $routeProvider, $mdThemingProvider, mtRoutesProvider) {
    $httpProvider.useLegacyPromiseExtensions = false;

    mtRoutesProvider.routes.main.forEach(function (route) {
        $routeProvider.when(route.href, {
            templateUrl: route.include,
            controller: route.controller
        });
    });

    mtRoutesProvider.routes.settings.forEach(function (route) {
        $routeProvider.when(route.href, {
            templateUrl: route.include,
            controller: route.controller
        });
    });

    $routeProvider.otherwise(mtRoutesProvider.routes.main[0].href);

    $mdThemingProvider.theme('default')
        .primaryPalette('blue-grey')
        .accentPalette('deep-purple');
});

app.run(function ($http, $rootScope, mtRoutes) {
    $rootScope.$on('$routeChangeSuccess', function(event, current, previous) {
        if(previous === undefined) {
            mtRoutes.prevRoute.set(current.originalPath);
            return;
        }
        mtRoutes.prevRoute.set(previous.originalPath);
    });
    
    if (!$http.defaults.headers.get) {
        $http.defaults.headers.get = {};
    }

    // Answer edited to include suggestions from comments
    // because previous version of code introduced browser-related errors

    //disable IE ajax request caching
    $http.defaults.headers.get['If-Modified-Since'] = 'Mon, 26 Jul 1997 05:00:00 GMT';
    // extra
    $http.defaults.headers.get['Cache-Control'] = 'no-cache';
    $http.defaults.headers.get.Pragma = 'no-cache';
});

var app = angular.module('myApp', []);

app.controller('MainController', function($scope, $http) {
    $scope.url = '';
    $scope.result = null;

    $scope.analyzeUrl = function() {
        $http.post('http://localhost:5000/analyze', { url: $scope.url })
            .then(function(response) {
                $scope.result = response.data;
            }, function(error) {
                console.error('Error:', error);
            });
    };
});

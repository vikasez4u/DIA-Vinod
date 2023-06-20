'use strict';

angular.module('myapp')
    .controller('modalOptionController', ['$scope', function($scope) {

    $scope.options=[
        {name:'Image', type:'imageOption'},
        {name:'Text', type:'textOption'}
    ]

}]);

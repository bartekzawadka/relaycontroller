angular.module('starter.controllers', [])

.controller('DashCtrl', function($scope, $http, $ionicLoading) {

  // 'Content-Type': 'application/json',
  //   'Accept': 'application/json'

  $scope.setState = function(state){
    //console.log(state);
    $http({
      url: 'http://192.168.1.115:8080/set_state',
      method: 'GET',
      params: {
        'value': state
      }
    }).then(function(response){
      //console.log(JSON.stringify(response));
      $scope.currentState = response.data;

    }, function(e){
      console.log('Error: '+e);
    });

  };

  var loadingFinished = function () {
    $ionicLoading.hide().then(function(){
      console.log("The loading indicator is now hidden");
      $scope.$broadcast('scroll.refreshComplete');
    });
  };

  $scope.loadData = function(){
    $ionicLoading.show({
      template: 'Zara!...'
    }).then(function(){
      // $scope.currentState = null;
      // $scope.states = null;

      $http({
        url: 'http://192.168.1.115:8080/get_alive_time',
        method: 'GET'
      }).then(function(response){
        $scope.waittime = response.data.value;

        $http({
          url: 'http://192.168.1.115:8080/get_state',
          method: 'GET'
        }).then(function(response){
          //console.log(JSON.stringify(response));
          $scope.currentState = 0;
          $scope.currentState = response.data;


      $http({
        url: 'http://192.168.1.115:8080/get_states',
        method: 'GET'
      }).then(function(response){
        //console.log(JSON.stringify(response));
        $scope.states = null;
        $scope.states = response.data;

        loadingFinished();

        }, function(e){
          console.log('Error: '+e);
          loadingFinished();
        });
      }, function(e){
        console.log('Error: '+e);
        loadingFinished();
      });
      }, function(e){
        console.log('Error: '+e);
        loadingFinished();
      });
    });
  };

  $scope.setTime = function(val){
    $http({
      url: 'http://192.168.1.115:8080/set_alive_time',
      method: 'GET',
      params: {
        'value': val
      }
    }).then(function(response){
      $scope.waittime = response.data.value;
    }, function(e){
      console.log('Error: '+e);
    });
  };

  var headers = {
    'Access-Control-Allow-Origin' : '*',
    'Access-Control-Allow-Methods' : 'POST, GET, OPTIONS, PUT'
  };

  $scope.loadData();
});

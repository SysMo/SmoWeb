$scope.inputPattern = /^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$/;
	//$scope.inputPattern = /^[0-9]$/;
		
$scope.UnitConverter.communicator = new ModelCommunicator();
	
$scope.UnitConverter.communicator.fetchData(
	'getQuantities', {}, function(comm){
		$scope.quantityData = comm.data;
		$scope.renderConverter();
	}
);

$scope.renderConverter = function() {
	$scope.quantities = {};
	for (name in $scope.quantityData) {
		var value = $scope.quantityData[name];
		if (value.SIUnit == '-')
			continue
		else {
			$scope.quantities[value.title] = new variables.Quantity(name, value.title, value.nominalValue, value.SIUnit, value.units);
		}
	}
	$scope.choiceVar = $scope.quantities[Object.keys($scope.quantities)[0]];
}
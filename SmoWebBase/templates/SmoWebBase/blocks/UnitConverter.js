$scope.inputPattern = /^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$/;
	//$scope.inputPattern = /^[0-9]$/;
		
$scope.UnitConverter.communicator = new communicator.Communicator();
	
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
			$scope.quantities[value.title] = new quantities.Quantity(name, value.title, value.nominalValue, value.SIUnit, value.units);
		}
	}
	$scope.choiceVar = $scope.quantities[Object.keys($scope.quantities)[0]];
}
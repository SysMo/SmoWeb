$scope.checks = 0;

onSuccessFunc = function(comm) {
	job = comm.data.job;
	if (comm.data.progressValue) {
		$scope.progressValue = comm.data.progressValue;
	} else {
		$scope.progressValue = 0;
	}
	$('#testBar').css('width', $scope.progressValue + "%");
	if ($scope.progressValue == 100) {
		return;
	}
	setTimeout(function(){
		if ($scope.checks < 500) {
			comm = new communicator.Communicator('/ThermoFluids/CheckProgress');
			comm.fetchData(undefined, job, onSuccessFunc);
			$scope.checks +=1;
		}
	}, 200);
	
	
}
progressCommunicator = new communicator.Communicator('/ThermoFluids/StartJob');
progressCommunicator.fetchData(undefined, undefined, onSuccessFunc);

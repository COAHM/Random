/// Finds all unique triplets that sum to zero.
List<List<int>> threeSum(List<int> nums) {
  nums.sort();
  Set<List<int>> result = {};

  for (int i = 0; i < nums.length - 2; i++) {
    int left = i + 1;
    int right = nums.length - 1;

    while (left < right) {
      int sum = nums[i] + nums[left] + nums[right];
      if (sum == 0) {
        result.add([nums[i], nums[left], nums[right]]);
        left++;
        right--;
      } else if (sum < 0) {
        left++;
      } else {
        right--;
      }
    }
  }

  return result.toList();
}
 // updated 1769353235

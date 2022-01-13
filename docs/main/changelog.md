# Changelog

## ;;VER v0.2.0;;

This version includes breaking change. The `align` method was renamed to `apply` and the `realign` method was renamed as `apply`.
Please update your codebase to reflect this!

- ;;remove;; removed the `quick_shifts` parameter as it was not really used and the `only_shift` parameter does the job instead
- ;;change;; the `align` method was renamed to `apply`
- ;;change;; the `realign` method was renamed to `align`
- ;;new;; added `compute` method which makes it possible to simply calculate the correction factors for signal that was not provided in the `array` attribute
- ;;change;; the `array` initialization value can now be `None` and it's assumed that you plan on using the `compute` method
- ;;new;; added `_align` and `_shift` methods that perform the correction methods. These can be handy if you are using the `compute` method
- ;;change;; all optional parameters are now properties with appropriate data validators


## ;;VER v0.1.10;;

- ;;new;; exposed few parameters to the `run` and `align` functions, so you can update the init parameters

## ;;VER v0.1.9;;

- ;;new;; exposed the post-alignment shift values (which might differ from `shift_opt` if the `quick_align` option is used)
- ;;improved;; tidied up code


## ;;VER v0.1.8;;

- ;;change;; Split the `run` command of the `Aligner` class to `run` (which computes the shift) and `align` which shifts
the input array to the new position.

## ;;VER v0.1.7;;

- ;;new;; Changed the structure of the package to be more Object-oriented. Alignment is now wrapped in its own class `Aligner` which can be directly
imported or used like before using `from msalign import msalign`
- ;;new;; Added new `shift` function which simply shifts signals without interpolation - can be a lot faster but less accurate. Can be accessed by using keyword parameter
`quick_shift=True` or by calling the `shift()` function
- ;;improved;; Cleaned-up code and renamed some poorly named variables
- ;;change;; Remove support from Python 2.7, 3.4, 3.5

## ;;VER v0.1.3;;

- ;;new;; added new keyword parameter `align_by_index` which when set to `True` will convert the values of `peaks` to index based on the input `xvals` array. This is introduced as I've noticed that sometimes when aligning to float values the alignment is not optimal
- ;;improved;; added more tests to the `tests` suite

## ;;VER v0.1.0;;

- ;;fix;; [#5](https://github.com/lukasz-migas/msalign/issues/5) small bug that prevented correct alignment of the MS example
- ;;new;; added new keyword parameter 'return_shifts' which when set to True will return the aligned data and the vector containing shift parameters

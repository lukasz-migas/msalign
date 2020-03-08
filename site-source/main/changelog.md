# Changelog

## Version 0.1.3

- New: added new keyword parameter `align_by_index` which when set to `True` will convert the values of `peaks` to index based on the input `xvals` array. This is introduced as I've noticed that sometimes when aligning to float values the alignment is not optimal
- Improved: added more tests to the `tests` suite

## Version 0.1.0

- Fixed: [#5](https://github.com/lukasz-migas/msalign/issues/5) small bug that prevented correct alignment of the MS example
- New: added new keyword parameter 'return_shifts' which when set to True will return the aligned data and the vector containing shift parameters

; Enable continuity probe
M746 S1
G38
; Set zero Z to current position
G92 Z0
M746 S0
; Disable continuity probe
G91
G0 Z2.0 F1000
; Turning spindle on
M3 S15000
G4 S3
; Spindle is on @ 15000 rpm
; Path #1
G0 X1.324 Y20.69943 F5000
G0 Z-2.35 F80
G0 X-0.16397 Y0.13172 F150
G0 X-0.14463 Y0.17624
G0 X-0.12512 Y0.26454
G0 X-0.04256 Y0.20408
G0 X-0.00608 Y0.1238
G0 X0.01852 Y0.18802
G0 X0.03012 Y0.12024
G0 X0.07229 Y0.17454
G0 X0.06373 Y0.10632
G0 X0.11985 Y0.14604
G0 X0.17785 Y0.1456
G0 X0.0 Y0.75886
G0 X-0.17785 Y0.1456
G0 X-0.11985 Y0.14604
G0 X-0.06373 Y0.10632
G0 X-0.07229 Y0.17454
G0 X-0.03012 Y0.12024
G0 X-0.01436 Y0.29229
G0 X0.04448 Y0.22361
G0 X0.12512 Y0.26454
G0 X0.14463 Y0.17624
G0 X0.16397 Y0.13172
G0 X0.0 Y1.64943
G0 X0.01116 Y0.11335
G0 X0.03307 Y0.10899
G0 X0.05369 Y0.10045
G0 X0.07225 Y0.08804
G0 X1.09983 Y1.09983
G0 X-0.0 Y2.35334
G0 X-0.2826 Y0.0
G0 X-0.07654 Y0.01522
G0 X-0.07806 Y0.0579
G0 X-0.04444 Y0.10728
G0 X0.0 Y2.0712
G0 X0.04444 Y0.10728
G0 X0.09654 Y0.06451
G0 X1.80486 Y0.00765
G0 X0.07468 Y-0.02266
G0 X0.06032 Y-0.0495
G0 X0.03018 Y-0.05034
G0 X0.01522 Y-0.07654
G0 X-0.00384 Y-2.07102
G0 X-0.04156 Y-0.08786
G0 X-0.09654 Y-0.06451
G0 X-0.34066 Y-0.00861
G0 X0.0 Y-2.594
G0 X-0.01593 Y-0.13239
G0 X-0.0719 Y-0.17356
G0 X-0.08234 Y-0.10488
G0 X-1.09983 Y-1.09983
G0 X0.0 Y-1.40877
G0 X0.17785 Y-0.1456
G0 X0.17432 Y-0.23505
G0 X0.08725 Y-0.21063
G0 X0.03686 Y-0.1853
G0 X0.00632 Y-0.11399
G0 X-0.00632 Y-0.11399
G0 X-0.03686 Y-0.1853
G0 X-0.08725 Y-0.21063
G0 X-0.17432 Y-0.23505
G0 X-0.17785 Y-0.1456
G0 X0.0 Y-0.75886
G0 X0.17785 Y-0.1456
G0 X0.17432 Y-0.23505
G0 X0.08725 Y-0.21063
G0 X0.03686 Y-0.1853
G0 X0.00632 Y-0.11399
G0 X-0.02259 Y-0.21708
G0 X-0.06235 Y-0.19892
G0 X-0.08906 Y-0.16661
G0 X-0.07384 Y-0.09956
G0 X-0.13359 Y-0.13359
G0 X-0.10117 Y-0.07481
G0 X0.0 Y-0.13877
G0 X3.46966 Y-3.46966
G0 X7.13868 Y0.0
G0 X3.299 Y3.299
G0 X-0.24834 Y0.0
G0 X-0.07654 Y0.01522
G0 X-0.07806 Y0.0579
G0 X-0.04444 Y0.10728
G0 X0.00765 Y2.07766
G0 X0.06451 Y0.09654
G0 X0.08786 Y0.04156
G0 X0.45802 Y0.00384
G0 X0.0 Y0.14
G0 X-0.47706 Y0.00861
G0 X-0.09654 Y0.06451
G0 X-0.04156 Y0.08786
G0 X-0.00384 Y2.03902
G0 X0.03371 Y0.11111
G0 X0.07201 Y0.06527
G0 X0.09428 Y0.02362
G0 X2.0 Y0.0
G0 X0.07654 Y-0.01522
G0 X0.05034 Y-0.03018
G0 X0.06451 Y-0.09654
G0 X-0.0 Y-2.11612
G0 X-0.06451 Y-0.09654
G0 X-0.08786 Y-0.04156
G0 X-0.45802 Y-0.00384
G0 X0.0 Y-0.14
G0 X0.47706 Y-0.00861
G0 X0.09654 Y-0.06451
G0 X0.04156 Y-0.08786
G0 X0.00384 Y-2.03902
G0 X-0.02362 Y-0.09428
G0 X-0.0495 Y-0.06032
G0 X-0.08786 Y-0.04156
G0 X-0.45802 Y-0.00384
G0 X-0.00828 Y-0.16393
G0 X-0.02933 Y-0.10993
G0 X-0.06031 Y-0.11893
G0 X-0.07225 Y-0.08804
G0 X-3.81 Y-3.81
G0 X-0.10488 Y-0.08234
G0 X-0.17356 Y-0.0719
G0 X-0.13239 Y-0.01593
G0 X-7.62 Y0.0
G0 X-0.11335 Y0.01116
G0 X-0.10899 Y0.03307
G0 X-0.10045 Y0.05369
G0 X-0.08804 Y0.07225
G0 X-3.82318 Y3.82454
G0 X-0.10437 Y0.15621
G0 X-0.04146 Y0.12673
G0 X-0.01116 Y0.49278
G0 Z2.35 F1000
; Turning spindle off
M5
G4 S3
; Spindle is off
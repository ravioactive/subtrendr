import matplotlib.pyplot as plt
import numpy as np
# data = [ [ 420, 684 ], [ 417, 683 ], [ 416, 681 ], [ 415, 680 ], [ 413, 679 ], [ 412, 678 ], [ 410, 677 ], [ 409, 676 ], [ 406, 675 ], [ 404, 673 ], [ 401, 671 ], [ 400, 670 ], [ 397, 669 ], [ 396, 667 ], [ 393, 665 ], [ 385, 664 ], [ 382, 663 ], [ 379, 662 ], [ 377, 661 ], [ 376, 660 ], [ 370, 659 ], [ 369, 657 ], [ 368, 656 ], [ 367, 655 ], [ 363, 654 ], [ 361, 652 ], [ 355, 651 ], [ 354, 649 ], [ 353, 647 ], [ 350, 646 ], [ 346, 643 ], [ 345, 642 ], [ 343, 641 ], [ 342, 640 ], [ 341, 639 ], [ 340, 637 ], [ 339, 636 ], [ 338, 634 ], [ 337, 632 ], [ 330, 631 ], [ 328, 630 ], [ 327, 629 ], [ 326, 628 ], [ 324, 625 ], [ 321, 624 ], [ 320, 622 ], [ 316, 620 ], [ 312, 618 ], [ 309, 617 ], [ 306, 616 ], [ 305, 614 ], [ 304, 613 ], [ 303, 612 ], [ 300, 611 ], [ 297, 610 ], [ 296, 609 ], [ 292, 607 ], [ 290, 606 ], [ 288, 604 ], [ 287, 603 ], [ 286, 602 ], [ 282, 601 ], [ 281, 600 ], [ 280, 599 ], [ 279, 597 ], [ 277, 596 ], [ 274, 595 ], [ 271, 594 ], [ 270, 592 ], [ 269, 591 ], [ 261, 590 ], [ 260, 589 ], [ 251, 588 ], [ 244, 587 ], [ 243, 586 ], [ 242, 585 ], [ 237, 584 ], [ 236, 583 ], [ 233, 581 ], [ 232, 580 ], [ 230, 579 ], [ 226, 576 ], [ 225, 574 ], [ 224, 571 ], [ 223, 570 ], [ 221, 569 ], [ 219, 568 ], [ 215, 567 ], [ 214, 562 ], [ 213, 560 ], [ 212, 557 ], [ 211, 556 ], [ 210, 554 ], [ 209, 553 ], [ 208, 552 ], [ 207, 551 ], [ 206, 549 ], [ 205, 548 ], [ 203, 546 ], [ 202, 545 ], [ 201, 544 ], [ 200, 542 ], [ 199, 541 ], [ 198, 539 ], [ 197, 538 ], [ 196, 535 ], [ 195, 533 ], [ 193, 532 ], [ 192, 530 ], [ 191, 527 ], [ 190, 525 ], [ 189, 522 ], [ 188, 519 ], [ 186, 515 ], [ 185, 512 ], [ 184, 511 ], [ 183, 506 ], [ 182, 503 ], [ 180, 501 ], [ 178, 500 ], [ 177, 498 ], [ 176, 496 ], [ 175, 495 ], [ 174, 494 ], [ 172, 493 ], [ 171, 492 ], [ 170, 491 ], [ 167, 489 ], [ 166, 488 ], [ 165, 485 ], [ 163, 484 ], [ 161, 482 ], [ 160, 480 ], [ 159, 479 ], [ 158, 478 ], [ 154, 476 ], [ 152, 475 ], [ 150, 474 ], [ 141, 472 ], [ 140, 470 ], [ 138, 469 ], [ 135, 467 ], [ 133, 466 ], [ 130, 465 ], [ 128, 464 ], [ 124, 463 ], [ 123, 462 ], [ 112, 460 ], [ 111, 459 ], [ 109, 458 ], [ 105, 456 ], [ 103, 455 ], [ 101, 454 ], [ 100, 453 ], [ 99, 452 ], [ 96, 451 ], [ 94, 450 ], [ 88, 449 ], [ 87, 447 ], [ 86, 446 ], [ 85, 445 ], [ 80, 443 ], [ 75, 442 ], [ 73, 441 ], [ 72, 439 ], [ 70, 438 ], [ 69, 437 ], [ 68, 435 ], [ 66, 433 ], [ 65, 432 ], [ 62, 431 ], [ 60, 430 ], [ 59, 429 ], [ 58, 428 ], [ 55, 427 ], [ 53, 426 ], [ 52, 425 ], [ 51, 424 ], [ 50, 423 ], [ 49, 421 ], [ 48, 419 ], [ 47, 418 ], [ 46, 415 ], [ 45, 414 ], [ 44, 413 ], [ 43, 412 ], [ 41, 409 ], [ 40, 408 ], [ 38, 407 ], [ 37, 404 ], [ 35, 403 ], [ 34, 401 ], [ 31, 399 ], [ 30, 398 ], [ 22, 397 ], [ 21, 396 ], [ 20, 395 ], [ 19, 394 ], [ 18, 392 ], [ 16, 391 ], [ 15, 388 ], [ 14, 387 ], [ 13, 386 ], [ 10, 384 ], [ 8, 383 ], [ 7, 382 ], [ 3, 381 ], [ 1, 380 ]]
slopedata = [ [ 437, 1.3554798410002062 ], [ 436, 1.5340632603417972 ], [ 435, 1.7051281990976441 ], [ 434, 1.8619528619547108 ], [ 430, 1.8502604166685157 ], [ 429, 1.6388286334070319 ], [ 428, 1.4607842910852842 ], [ 427, 1.275938189846081 ], [ 426, 1.1153846153848712 ], [ 425, 0.9608985024957544 ], [ 424, 0.8198594024600604 ], [ 422, 0.7142857142851068 ], [ 421, 0.6889279437602989 ], [ 420, 0.6889279437602989 ], [ 419, 0.683717297929805 ], [ 418, 0.683717297929805 ], [ 417, 0.683717297929805 ], [ 416, 0.6588072122045214 ], [ 415, 0.6365552544406412 ], [ 414, 0.664519906322453 ], [ 413, 0.664519906322453 ], [ 412, 0.6804068522477011 ], [ 410, 0.5747795083496041 ], [ 409, 0.502996642862242 ], [ 406, 0.4510794091643142 ], [ 404, 0.4055606617634072 ], [ 401, 0.384650743064634 ], [ 400, 0.3528194516281833 ], [ 397, 0.3530673586996921 ], [ 396, 0.3513353115712964 ], [ 394, 0.38729763387163985 ], [ 393, 0.38729763387163985 ], [ 390, 0.47267292911926295 ], [ 385, 0.47267292911926295 ], [ 382, 0.5145586897168666 ], [ 379, 0.48878047058412327 ], [ 377, 0.4981818193090938 ], [ 376, 0.5329385640256222 ], [ 370, 0.5674603174593752 ], [ 369, 0.5657181571806255 ], [ 368, 0.5872703412064475 ], [ 367, 0.6115787665341142 ], [ 365, 0.6651376146781707 ], [ 363, 0.6651376146781707 ], [ 362, 0.6919191736374467 ], [ 361, 0.6919191736374467 ], [ 357, 0.7978539286946101 ], [ 355, 0.7978539286946101 ], [ 354, 0.7881583841870089 ], [ 353, 0.8415841584154943 ], [ 352, 1.0420979496281826 ], [ 350, 1.0420979496281826 ], [ 349, 0.8602435150870466 ], [ 348, 0.8602435150870466 ], [ 346, 0.8602435150870466 ], [ 345, 0.7362924281978542 ], [ 343, 0.6797488226052706 ], [ 342, 0.6353467561513257 ], [ 341, 0.6333333333325335 ], [ 340, 0.6023255771431559 ], [ 339, 0.6186046511619603 ], [ 338, 0.6242994844197101 ], [ 337, 0.649175412293097 ], [ 336, 0.7038435938389945 ], [ 333, 0.7038435938389945 ], [ 330, 0.7038435938389945 ], [ 328, 0.6387729170440388 ], [ 327, 0.6150558985162603 ], [ 326, 0.5970961887468524 ], [ 325, 0.5790441176461365 ], [ 324, 0.5790441176461365 ], [ 321, 0.5834703947359274 ], [ 320, 0.549388107704298 ], [ 318, 0.5669247787601233 ], [ 317, 0.5669247787601233 ], [ 316, 0.5669247787601233 ], [ 315, 0.5730140186906569 ], [ 314, 0.5730140186906569 ], [ 312, 0.5730140186906569 ], [ 311, 0.5680539932499101 ], [ 309, 0.5680539932499101 ], [ 306, 0.568816928381759 ], [ 305, 0.5574092247291573 ], [ 304, 0.5774930921869761 ], [ 303, 0.5763086734174275 ], [ 302, 0.6070543116647267 ], [ 300, 0.6070543116647267 ], [ 298, 0.630605225672257 ], [ 297, 0.630605225672257 ], [ 296, 0.6617179215263025 ], [ 294, 0.703799654576214 ], [ 292, 0.703799654576214 ], [ 291, 0.6798679867979898 ], [ 290, 0.6798679867979898 ], [ 289, 0.6122082740345666 ], [ 288, 0.6122082740345666 ], [ 287, 0.6221259580131752 ], [ 286, 0.647661317855152 ], [ 282, 0.5444555444545405 ], [ 281, 0.4852472089302897 ], [ 280, 0.3711077080129185 ], [ 279, 0.2879563312881828 ], [ 278, 0.264192139736384 ], [ 277, 0.264192139736384 ], [ 276, 0.25411847178245917 ], [ 274, 0.25411847178245917 ], [ 271, 0.23961365440426985 ], [ 270, 0.2307276535352537 ], [ 269, 0.2526347485680781 ], [ 265, 0.30330637731447774 ], [ 264, 0.30330637731447774 ], [ 262, 0.30330637731447774 ], [ 261, 0.30330637731447774 ], [ 260, 0.3446775844407519 ], [ 254, 0.4926413632831612 ], [ 253, 0.4926413632831612 ], [ 251, 0.4926413632831612 ], [ 250, 0.6202107300550788 ], [ 247, 0.6202107300550788 ], [ 246, 0.6202107300550788 ], [ 245, 0.6202107300550788 ], [ 244, 0.6202107300550788 ], [ 243, 0.7075195312500018 ], [ 242, 0.809181415928802 ], [ 240, 0.9548767950490173 ], [ 239, 0.9548767950490173 ], [ 238, 0.9548767950490173 ], [ 237, 0.9548767950490173 ], [ 236, 0.9615521261849426 ], [ 235, 0.8829499359159396 ], [ 233, 0.8829499359159396 ], [ 232, 0.9310456458399258 ], [ 231, 0.9999999999999974 ], [ 230, 0.9999999999999974 ], [ 229, 1.0845070391523275 ], [ 226, 1.0845070391523275 ], [ 225, 1.1105863833139005 ], [ 224, 1.1666666666670282 ], [ 223, 1.2896652110632234 ], [ 221, 1.4624060150386096 ], [ 220, 1.6241496576146097 ], [ 219, 1.6241496576146097 ], [ 215, 1.7757576282703613 ], [ 214, 1.4909090909101514 ], [ 213, 1.3376623376630723 ], [ 212, 1.2157842157846885 ], [ 211, 1.1780303030306867 ], [ 210, 1.1717171717175505 ], [ 209, 1.190909090909518 ], [ 208, 1.236914600551492 ], [ 207, 1.255681818182374 ], [ 206, 1.3396603396610818 ], [ 205, 1.497835497836588 ], [ 203, 1.5367965367977166 ], [ 202, 1.5514485514497414 ], [ 201, 1.6174242169524935 ], [ 200, 1.6602387511492833 ], [ 199, 1.7727272727289554 ], [ 198, 1.8916437098274637 ], [ 197, 2.0223944875129956 ], [ 196, 2.1350210970488845 ], [ 195, 2.241171403964809 ], [ 194, 2.5078052974615535 ], [ 193, 2.5078052974615535 ], [ 192, 2.590909094559516 ], [ 191, 2.4849498327791357 ], [ 190, 2.234432234434937 ], [ 189, 2.030219780222042 ], [ 188, 1.8795098706622362 ], [ 186, 1.7293447293463204 ], [ 185, 1.5712250712263123 ], [ 184, 1.3703199455419868 ], [ 183, 1.1304945344958777 ], [ 182, 1.0293040175287091 ], [ 180, 0.9583333333332263 ], [ 178, 0.9081365039192282 ], [ 177, 0.9122486407641296 ], [ 176, 0.9049198640642568 ], [ 175, 0.937125748502851 ], [ 174, 1.0043923813650615 ], [ 173, 1.0740740740742392 ], [ 172, 1.0740740740742392 ], [ 171, 1.102150537634629 ], [ 170, 1.0350792888035363 ], [ 168, 0.948314606741464 ], [ 167, 0.948314606741464 ], [ 166, 0.8302752293574271 ], [ 165, 0.5699202758016977 ], [ 164, 0.5223123942472253 ], [ 163, 0.5223123942472253 ], [ 161, 0.48047831724422085 ], [ 160, 0.4636010524985211 ], [ 159, 0.46208531562692967 ], [ 158, 0.45790530168733057 ], [ 156, 0.46297025548234655 ], [ 155, 0.46297025548234655 ], [ 154, 0.46297025548234655 ], [ 152, 0.45676005366346895 ], [ 151, 0.46643445218375745 ], [ 150, 0.46643445218375745 ], [ 149, 0.4022453450151322 ], [ 148, 0.4022453450151322 ], [ 146, 0.4022453450151322 ], [ 144, 0.4022453450151322 ], [ 141, 0.4022453450151322 ], [ 140, 0.35493144626130546 ], [ 139, 0.3381236716917049 ], [ 138, 0.3381236716917049 ], [ 137, 0.332706766915836 ], [ 136, 0.332706766915836 ], [ 135, 0.332706766915836 ], [ 134, 0.34104258443320956 ], [ 133, 0.34104258443320956 ], [ 132, 0.35477657935144924 ], [ 130, 0.35477657935144924 ], [ 128, 0.37386413598252016 ], [ 127, 0.41035474592393695 ], [ 124, 0.41035474592393695 ], [ 123, 0.4422179996532968 ], [ 121, 0.5523255809482932 ], [ 119, 0.5523255809482932 ], [ 117, 0.5523255809482932 ], [ 116, 0.5523255809482932 ], [ 114, 0.5523255809482932 ], [ 112, 0.5523255809482932 ], [ 111, 0.47351301115126143 ], [ 110, 0.4693060498209095 ], [ 109, 0.4693060498209095 ], [ 108, 0.47400326416299143 ], [ 105, 0.47400326416299143 ], [ 103, 0.4876441515639528 ], [ 102, 0.48922056384631807 ], [ 101, 0.48922056384631807 ], [ 100, 0.45514950165993817 ], [ 99, 0.4414997741291814 ], [ 96, 0.47005044606429813 ], [ 95, 0.48996655518284427 ], [ 94, 0.48996655518284427 ], [ 88, 0.5220372184122768 ], [ 87, 0.5290519877665594 ], [ 86, 0.5766129032248871 ], [ 85, 0.650098286997272 ], [ 84, 0.7822580645156375 ], [ 80, 0.7822580645156375 ], [ 79, 0.8653846153843237 ], [ 78, 0.8653846153843237 ], [ 77, 0.8653846153843237 ], [ 76, 0.8653846153843237 ], [ 75, 0.8653846153843237 ], [ 74, 0.8255597014921665 ], [ 73, 0.8255597014921665 ], [ 72, 0.7729556875280519 ], [ 71, 0.7112794612788329 ], [ 70, 0.7112794612788329 ], [ 69, 0.6341463414626147 ], [ 68, 0.5787923416780276 ], [ 66, 0.5674179517586537 ], [ 65, 0.5921908973123473 ], [ 63, 0.6850185283211951 ], [ 62, 0.6850185283211951 ], [ 60, 0.7867867867863143 ], [ 59, 0.8756684491975812 ], [ 58, 1.0776621473741885 ], [ 55, 1.3939393939402454 ], [ 54, 1.5515151515163486 ], [ 53, 1.5515151515163486 ], [ 52, 1.5636363636375876 ], [ 51, 1.545454545455721 ], [ 50, 1.4825174825185228 ], [ 49, 1.3036783575712514 ], [ 48, 1.2715283397790351 ], [ 47, 1.1940700962394137 ], [ 46, 1.150530918176457 ], [ 45, 1.111691022964757 ], [ 44, 1.0802498798656124 ], [ 43, 0.7658354829458768 ], [ 41, 0.634470118971231 ], [ 40, 0.5786061588321403 ], [ 39, 0.5360047885604833 ], [ 38, 0.5360047885604833 ], [ 37, 0.5053850843313685 ], [ 35, 0.5092024668775353 ], [ 34, 0.5454545454535659 ], [ 31, 0.6333771353474217 ], [ 30, 0.7797834201202712 ], [ 27, 1.167664686033441 ], [ 26, 1.167664686033441 ], [ 24, 1.167664686033441 ], [ 23, 1.167664686033441 ], [ 22, 1.167664686033441 ], [ 21, 1.0681265206813997 ], [ 20, 0.9999999999999998 ], [ 19, 0.8271553519363366 ], [ 18, 0.6953528399304755 ], [ 16, 1.41204330176003 ], [ 15, 1.6349337748358066 ], [ 14, 1.9221748995202779 ], [ 13, 2.3598841419290872 ], [ 12, 2.9328703703745878 ], [ 10, 2.9328703703745878 ], [ 9, 3.167471819650459 ], [ 8, 3.167471819650459 ] ]
# npdata = np.array(data)
# xdata = npdata[:,0]
# ydata = npdata[:,1]
snpdata = np.array(slopedata)
sxdata = snpdata[:,0]
sydata = snpdata[:,1]
plt.plot(sxdata, sydata)
# plt.plot(sxdata, sydata)
# plt.axis([0, 6, 0, 20])
plt.show()
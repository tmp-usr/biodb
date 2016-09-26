from taxon import Taxon
from lineage import Lineage
from lineage_pruner import LineagePruner

from biodb.sqling.selector import Selector, Hierarchy, BioDB

import pdb

import logging

from paketbuiol.io_helper import BatchReader

class Controller(object):
    
    def __init__(self, biodb_selector, lineage_types_file_path="" ):
        
        #self.set_logger()

        handle= biodb_selector.getFeaturesByLevel(6, 100)        
        

        i=0 
        for chunk in handle:
            for chain in chunk:  
                for feature in chain:

                    self.feature= feature
                    try:
                        self.lineage= Lineage(feature, biodb_selector)
                    except:
                        continue

                    lin_type= self.lineage.lineage_type
                    

                    print lin_type
                    #i+=1
                    #if lin_type == 1:
                    #    continue
                    
                    #self.lineage_pruner= LineagePruner(self.lineage, lin_type)
                    
                    #log= "lineage type: %s" %lin_type

                    #self.logger.info(log)

                    if lin_type == 2:
                        ### prune unnecessary
                        #print lin_type 
                        #if len(self.lineage.taxon_list)  == 6 :
                        #    pdb.set_trace()
                        

                        #print len([t.level for t in self.lineage.taxon_list])
                        pass
                        #self.lineage_pruner.prune_unnecessary()
                        
                        #self.logger.info([t.level for t in self.lineage.taxon_list])
                
                    elif lin_type == 3:
                        ### update unnecessary and prune
                        pass
                        #self.lineage_pruner.use_unnecessary_and_prune()
                        #pass
                        #self.lineage_pruner.prune_unnecessary(use=True)
                    
                    elif lin_type == 4:
                        ### TODO!: find a way to deal with!
                        pass

                    #print i, self.feature.id, self.feature.name
                
                    #    print i
                    #if i % 10000 == 0:
                    #    print "########## %d taxa processed ##########" %i


    def set_logger(self):
        # create logger with "spam application"
        self.logger= logging.getLogger("dev")
        self.logger.setLevel(logging.DEBUG)

        # create a file handler 
        fh= logging.FileHandler("ncbi_taxonomy.log", mode= "w")
        fh.setLevel(logging.DEBUG)

        # create a console handler
        #ch= logging.StreamHandler()
        #ch.setLevel(logging.DEBUG)

        # set formatter
        #formatter = logging.Formatter("%(asctime)s - %(name)s- %(levelname)s - %(message)s", 
        #        datefmt='%m/%d/%Y %I:%M:%S %p')
        
        formatter = logging.Formatter("%(message)s")
               
        
        fh.setFormatter(formatter)
        #ch.setFormatter(formatter)

        # add handlers to the logger
        self.logger.addHandler(fh)
        #self.logger.addHandler(ch)

                
        #print "%d\t%s\t%d" %(feature.id, feature.name, self.lineage.lineage_type)

        #print self.lineage.taxon_list
        #self.lineage_pruner= LineagePruner(self.lineage)
        #self.lineage_pruner.auto_prune()
        
        #print self.lineage_pruner.lineage.taxon_list

#lineage_types_file_path= "/Users/kemal/shared/repos/dev/biodb/biodb/ncbi_taxonomy/ncbi_taxonomy_lineage_types.txt"

s= Selector("ncbi")

Controller(s)


#species_taxa= s.getFeaturesByLevel(6)
#mock_taxa_2= species_taxa[:2500]

#for taxon in mock_taxa_2:
#    lineage= getTaxonomy(taxon)
#    if len(lineage) > 7:
#        print taxon.id

#tax_ids= [786, 1037, 301, 154, 151]

#tax_ids = [33,34,35,38,41,43,45,48,51,52,54,56,57,301,316,317,330,358,380,781,782,783,785,786,787,788,789]

#tax_ids= [33,34,35,38,41,43,45,48,51,52,54,56,57,301,316,317,330,358,380,781,782,783,785,786,787,788,789,1037,1884,1892,1908,1911,1919,1944,2057,2708,2709,2711,2959,3197,3203,3207,3213,3218,3222,3225,3229,3231,3234,3240,3247,3252,3258,3259,3260,3261,3262,3267,3271,3274,3277,3279,3281,3284,3285,3288,3289,3300,3301,3302,3304,3305,3306,3307,3311,3316,3317,3320,3322,3324,3326,3327,3329,3330,3331,3332,3333,3334,3335,3336,3338,3339,3340,3341,3342,3343,3344,3345,3346,3347,3348,3349,3350,3351,3352,3353,3355,3357,3359,3366,3369,3371,3377,3381,3382,3383,3388,3389,3390,3391,3396,3397,3403,3404,3406,3407,3408,3409,3410,3411,3412,3414,3415,3419,3420,3422,3423,3426,3429,3430,3431,3435,3436,3438,3442,3444,3447,3449,3451,3453,3454,3457,3460,3464,3467,3469,3472,3476,3477,3480,3483,3485,3486,3489,3490,3492,3494,3496,3498,3501,3505,3507,3508,3510,3512,3513,3516,3517,3522,3523,3527,3528,3530,3533,3535,3538,3541,3544,3546,3548,3551,3552,3553,3557,3559,3560,3562,3565,3567,3570,3572,3575,3578,3580,3583,3586,3589,3592,3595,3597,3600,3604,3605,3607,3610,3613,3617,3619,3621,3625,3627,3631,3634,3635,3636,3638,3641,3645,3649,3652,3654,3656,3659,3661,3662,3663,3668,3670,3672,3673,3674,3675,3677,3679,3682,3685,3690,3691,3693,3694,3695,3696,3697,3702,3704,3707,3708,3710,3711,3712,3717,3719,3724,3726,3728,3730,3732,3735,3741,3743,3747,3750,3751,3752,3755,3758,3759,3760,3762,3763,3765,3767,3770,3772,3775,3778,3780,3785,3791,3795,3797,3799,3802,3806,3809,3811,3813,3816,3818,3821,3823,3824,3825,3827,3829,3830,3832,3834,3835,3837,3838,3842,3843,3844,3845,3847,3848,3850,3852,3854,3855,3856,3857,3858,3859,3860,3861,3862,3864,3866,3868,3870,3871,3872,3873,3874,3876,3878,3879,3880,3882,3884,3885,3886,3888,3890,3891,3895,3897,3899,3900,3902,3905,3906,3908,3910,3911,3912,3914,3915,3917,3918,3922,3926,3930,3933,3936,3937,3938,3940,3941,3942,3945,3946,3948,3949,3950,3951,3953,3956,3960,3962,3965,3966,3968,3970,3972,3975,3979,3981,3983,3985,3986,3988,3991,3992,3993,3994,3996,3999,4002,4006,4009,4013,4016,4020,4023,4024,4025,4026,4029,4031,4032,4035,4039,4041,4043,4045,4047,4049,4052,4054,4058,4060,4062,4066,4068,4072,4073,4075,4076,4079,4081,4082,4083,4084,4086,4087,4089,4090,4091,4092,4093,4094,4096,4097,4098,4100,4102,4103,4104,4108,4109,4110,4111,4112,4113,4114,4115,4116,4120,4121,4123,4124,4129,4132,4134,4138,4142,4146,4151,4153,4155,4156,4157,4158,4159,4160,4161,4162,4164,4166,4168,4170,4172,4174,4177,4179,4182,4184,4187,4189,4191,4193,4195,4198,4202,4203,4205,4208,4212,4214,4217,4218,4220,4222,4224,4225,4226,4227,4228,4230,4232,4233,4234,4236,4238,4240,4243,4245,4247,4249,4250,4252,4254,4255,4256,4258,4260,4261,4263,4265,4270,4273,4276,4278,4282,4283,4284,4285,4288,4292,4296,4297,4298,4299,4300,4302,4304,4307,4309,4312,4315,4318,4320,4323,4326,4330,4332,4337,4341,4344,4347,4349,4351,4355,4357,4359,4362,4364,4365,4366,4367,4368,4369,4370,4371,4373,4376,4378,4383,4388,4392,4396,4397,4400,4403,4407,4412,4414,4416,4419,4421,4424,4426,4428,4431,4432,4436,4442,4443,4451,4452,4456,4458,4460,4463,4465,4467,4470,4472,4477,4481,4483,4485,4486,4487,4491,4492,4493,4494,4497,4498,4499,4500,4502,4505,4509,4511,4513,4515,4516,4517,4519,4521,4522,4524,4525,4528,4529,4530,4532,4533,4534,4535,4536,4537,4538,4540,4543,4545,4547,4550,4551,4552,4553,4555,4556,4558,4560,4563,4565,4566,4568,4569,4570,4571,4572,4573,4576,4577,4580,4582,4584,4586,4588,4589,4591,4593,4595,4597,4601,4603,4604,4606,4607,4608,4611,4615,4617,4621,4623,4625,4628,4629,4632,4634,4636,4639,4641,4644,4646,4647,4649,4651,4654,4655,4658,4662,4664,4666,4670,4673,4676,4679,4681,4682,4683,4684,4686,4689,4690,4691,4692,4694,4696,4698,4700,4702,4705,4707,4712,4714,4716,4718]



#for tax_id in tax_ids:
#    feature= s.getFeatureByID(tax_id)


#all_species= s.getFeaturesByLevel(6)

#feature= s.getFeatureByID(258)

#for feature in all_species:
#    Controller(feature, s)
    

#level_range= [25,11,2,11,11,4,11,11,11,11]

#c= Controller(level_range)
#lp= c.auto_prune()

#print c.lineage.taxon_list
#print c.lineage_pruner.logger.default_lineage
#print c.lineage_pruner.logger.updated_lineage


#c.lineage


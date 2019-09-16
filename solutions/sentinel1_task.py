class ReactivTask(EOTask):
    
    def __init__(self, 
                 reactiv_feature=(FeatureType.DATA_TIMELESS, 'specle_variability'), 
                 data_feature=(FeatureType.DATA, 'IW_VV'), 
                 mask_feature=(FeatureType.MASK, 'IS_DATA')):
        self.reactiv_feature = reactiv_feature
        self.data_feature = data_feature
        self.mask_feature = mask_feature
    
    def specle_variability(self, eopatch):
    
        eopatch_size = eopatch[self.data_feature][0][...,0].shape
        time_delta = np.max(eopatch.timestamp) - np.min(eopatch.timestamp)
        min_time = np.min(eopatch.timestamp)
        time = (np.array(eopatch.timestamp)-min_time)/time_delta

        masked_eopatch = np.ma.array(eopatch[self.data_feature].squeeze(), 
                                     mask=np.logical_not(eopatch[self.mask_feature].squeeze()))

        mb1 = masked_eopatch.mean(axis=0) #M1
        mb2 = np.ma.power(masked_eopatch, 2).mean(axis=0) #M2
        kmax = time[masked_eopatch.argmax(axis=0).ravel()].reshape(eopatch_size).astype(np.float32)
        imax = eopatch[self.data_feature].squeeze().max(axis=0) #Imax

        R = np.sqrt(mb2-mb1**2)/mb1

        gam = R.mean()
        a = 0.991936+0.067646*gam-0.098888*gam**2 -0.048320*gam**3
        b = 0.001224-0.034323*gam+4.305577*gam**2-1.163498*gam**3
        L = a/b;

        CV = np.sqrt((L*gamma(L)**2/(gamma(L+0.5)**2))-1); # theretical mean value
        num = (L*gamma(L)**4.*(4*(L**2)*gamma(L)**2-4*L*gamma(L+1/2)**2-gamma(L+1/2)**2));
        den = (gamma(L+1/2)**4.*(L*gamma(L)**2-gamma(L+1/2)**2));
        alpha = 1/4*num/den; # theretical standard deviation value

        R = (R-CV)/(alpha/np.sqrt(np.count_nonzero(eopatch[self.data_feature], axis=0).squeeze()))/10.0+0.25; 
        R = np.clip(R.data, a_min=0, a_max=1);   # Cast Coefficient of Varation R max to 1.

        threshold = np.mean(masked_eopatch[0]) + 15*np.std(masked_eopatch[0])
        I = np.clip(imax/threshold, a_max=1, a_min=0); # normalize Intensity to threshold. 

        hsv = np.stack([kmax, R.data, I], axis=2).astype(np.float32)

        return hsv
    
    def execute(self, eopatch):
        
        eopatch[self.reactiv_feature] = self.specle_variability(eopatch)
        
        return eopatch
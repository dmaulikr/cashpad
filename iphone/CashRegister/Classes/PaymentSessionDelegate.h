//
//  PaymentSessionDelegate.h
//  CashRegister
//
//  Created by Rits Plasman on 19-02-11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>

@class PaymentSession;
@class PaymentRequest;

@protocol PaymentSessionDelegate <NSObject>

@optional

- (void)paymentSession:(PaymentSession *)session didReceivePaymentRequest:(PaymentRequest *)request;
- (void)paymentSession:(PaymentSession *)session didAcceptPaymentRequest:(PaymentRequest *)request;
- (void)paymentSession:(PaymentSession *)session didDenyPaymentRequest:(PaymentRequest *)request;

@end

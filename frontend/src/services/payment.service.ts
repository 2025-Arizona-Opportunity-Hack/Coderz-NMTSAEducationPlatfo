import type {
  CreatePaymentOrderResponse,
  CapturePaymentOrderResponse,
  Payment,
  ApiResponse,
} from "../types/api";

import api from "../config/api";

export const paymentService = {
  /**
   * Create a PayPal order for course payment
   */
  async createOrder(courseId: string): Promise<CreatePaymentOrderResponse> {
    const response = await api.post<CreatePaymentOrderResponse>(
      "/student/payments/create-order/",
      { course_id: courseId },
    );

    return response.data;
  },

  /**
   * Capture a PayPal payment order
   */
  async captureOrder(orderId: string): Promise<CapturePaymentOrderResponse> {
    const response = await api.post<CapturePaymentOrderResponse>(
      "/student/payments/capture-order/",
      { order_id: orderId },
    );

    return response.data;
  },

  /**
   * Get payment history for current user
   */
  async getPaymentHistory(): Promise<Payment[]> {
    const response =
      await api.get<ApiResponse<Payment[]>>("/student/payments/");

    return response.data.data;
  },
};
